from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from usuarios.models import UsuarioSede
from usuarios.decorators import vendedor_required
from ventas.models import Caja, AperturaCaja


def obtener_caja_abierta(usuario):
    return AperturaCaja.objects.filter(
        usuario=usuario,
        estado='ABIERTA'
    ).select_related(
        'caja',
        'caja__sede'
    ).first()


def es_admin(usuario):
    return (
        usuario.is_superuser
        or usuario.groups.filter(name='Administrador').exists()
    )


@vendedor_required
def abrir_caja(request):
    caja_abierta = obtener_caja_abierta(request.user)

    if caja_abierta:
        return redirect('ventas:pos_venta')

    if es_admin(request.user):
        cajas = Caja.objects.filter(
            activa=True
        ).select_related(
            'sede'
        ).order_by(
            'sede__nombre',
            'nombre'
        )
    else:
        usuario_sede = UsuarioSede.objects.filter(
            usuario=request.user
        ).select_related(
            'sede'
        ).first()

        if not usuario_sede:
            messages.error(
                request,
                'No tienes una sede asignada.'
            )
            return redirect('home')

        cajas = Caja.objects.filter(
            activa=True,
            sede=usuario_sede.sede
        ).select_related(
            'sede'
        ).order_by(
            'nombre'
        )

    cajas = list(cajas)

    cajas_ocupadas = list(
        AperturaCaja.objects.filter(
            estado='ABIERTA'
        ).values_list(
            'caja_id',
            flat=True
        )
    )

    caja_inicial_id = next(
        (caja.id for caja in cajas if caja.id not in cajas_ocupadas),
        None
    )

    if request.method == 'POST':
        caja_id = request.POST.get('caja')
        turno = request.POST.get('turno')
        monto_inicial = request.POST.get('monto_inicial') or '0'

        if not caja_id:
            messages.error(
                request,
                'Selecciona una caja disponible.'
            )
            return redirect('ventas:abrir_caja')

        caja = next(
            (item for item in cajas if str(item.id) == str(caja_id)),
            None
        )

        if not caja:
            messages.error(
                request,
                'La caja seleccionada no está disponible para tu usuario.'
            )
            return redirect('ventas:abrir_caja')

        if caja.id in cajas_ocupadas:
            messages.error(
                request,
                'Esta caja ya está ocupada.'
            )
            return redirect('ventas:abrir_caja')

        turnos_validos = dict(AperturaCaja.TURNO_CHOICES)

        if turno not in turnos_validos:
            messages.error(
                request,
                'Selecciona un turno válido.'
            )
            return redirect('ventas:abrir_caja')

        try:
            monto_inicial = Decimal(str(monto_inicial))
        except (InvalidOperation, TypeError):
            messages.error(
                request,
                'El monto inicial no es válido.'
            )
            return redirect('ventas:abrir_caja')

        if monto_inicial < 0:
            messages.error(
                request,
                'El monto inicial no puede ser negativo.'
            )
            return redirect('ventas:abrir_caja')

        AperturaCaja.objects.create(
            caja=caja,
            usuario=request.user,
            turno=turno,
            monto_inicial=monto_inicial
        )

        messages.success(
            request,
            'Caja abierta correctamente.'
        )

        return redirect('ventas:pos_venta')

    return render(
        request,
        'ventas/caja/abrir_caja.html',
        {
            'cajas': cajas,
            'cajas_ocupadas': cajas_ocupadas,
            'caja_inicial_id': caja_inicial_id,
        }
    )


@vendedor_required
def cerrar_caja(request):
    apertura = obtener_caja_abierta(request.user)

    if not apertura:
        messages.error(
            request,
            'No tienes una caja abierta.'
        )

        return redirect(
            'ventas:abrir_caja'
        )

    ingresos = apertura.movimientos.filter(tipo='INGRESO').aggregate(
        total=Sum('monto'),
        cantidad=Count('id')
    )

    salidas = apertura.movimientos.filter(tipo='SALIDA').aggregate(
        total=Sum('monto'),
        cantidad=Count('id')
    )

    ingresos_total = ingresos.get('total') or Decimal('0.00')
    salidas_total = salidas.get('total') or Decimal('0.00')
    ingresos_count = ingresos.get('cantidad') or 0
    salidas_count = salidas.get('cantidad') or 0
    monto_esperado = apertura.monto_inicial + ingresos_total - salidas_total

    contexto = {
        'apertura': apertura,
        'ingresos': ingresos_total,
        'salidas': salidas_total,
        'ingresos_total': ingresos_total,
        'salidas_total': salidas_total,
        'ingresos_count': ingresos_count,
        'salidas_count': salidas_count,
        'movimientos_count': ingresos_count + salidas_count,
        'monto_esperado': monto_esperado,
        'monto_esperado_js': format(monto_esperado, '.2f'),
    }

    if request.method == 'POST':
        monto_contado = request.POST.get('monto_contado')

        if monto_contado in (None, ''):
            messages.error(
                request,
                'Ingresa el monto contado en caja.'
            )
            return render(
                request,
                'ventas/caja/cerrar_caja.html',
                contexto
            )

        try:
            monto_contado = Decimal(
                str(monto_contado).replace(',', '.')
            )
        except (InvalidOperation, TypeError):
            messages.error(
                request,
                'El monto contado no es válido.'
            )
            return render(
                request,
                'ventas/caja/cerrar_caja.html',
                contexto
            )

        if monto_contado < 0:
            messages.error(
                request,
                'El monto contado no puede ser negativo.'
            )
            return render(
                request,
                'ventas/caja/cerrar_caja.html',
                contexto
            )

        apertura.cerrar(
            monto_contado
        )

        messages.success(
            request,
            'Caja cerrada correctamente.'
        )

        return redirect(
            'ventas:pos_venta'
        )

    return render(
        request,
        'ventas/caja/cerrar_caja.html',
        contexto
    )
