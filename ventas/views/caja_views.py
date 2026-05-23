from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

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

    cajas_ocupadas = AperturaCaja.objects.filter(
        estado='ABIERTA'
    ).values_list(
        'caja_id',
        flat=True
    )

    if request.method == 'POST':
        caja_id = request.POST.get('caja')
        turno = request.POST.get('turno')
        monto_inicial = request.POST.get('monto_inicial') or 0

        caja = get_object_or_404(
            Caja,
            id=caja_id,
            activa=True
        )

        if AperturaCaja.objects.filter(
            caja=caja,
            estado='ABIERTA'
        ).exists():
            messages.error(
                request,
                'Esta caja ya está ocupada.'
            )
            return redirect('ventas:abrir_caja')

        AperturaCaja.objects.create(
            caja=caja,
            usuario=request.user,
            turno=turno,
            monto_inicial=Decimal(str(monto_inicial))
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
            'cajas_ocupadas': list(cajas_ocupadas),
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

    monto_esperado = apertura.calcular_monto_esperado()

    if request.method == 'POST':
        monto_contado = request.POST.get('monto_contado') or 0

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
        {
            'apertura': apertura,
            'monto_esperado': monto_esperado
        }
    )