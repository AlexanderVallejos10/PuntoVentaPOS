from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from productos.models import Producto
from ventas.models import Venta
from ventas.models import MovimientoCaja
from ventas.models import AperturaCaja
from ventas.models import DetalleVenta


def es_admin_o_super(usuario):
    return (
        usuario.is_superuser
        or usuario.groups.filter(
            name='Administrador'
        ).exists()
    )


def decimal_float(valor):
    return float(
        valor
        or
        Decimal('0.00')
    )


@login_required
def home(request):

    hoy = timezone.localdate()
    anio_actual = hoy.year
    mes_actual = hoy.month

    ventas = Venta.objects.all()
    movimientos = MovimientoCaja.objects.all()
    aperturas = AperturaCaja.objects.all()

    detalles = DetalleVenta.objects.select_related(
        'venta',
        'producto',
        'producto__categoria'
    )

    es_admin = es_admin_o_super(
        request.user
    )

    if not es_admin:

        ventas = ventas.filter(
            movimientocaja__apertura__usuario=request.user
        ).distinct()

        movimientos = movimientos.filter(
            apertura__usuario=request.user
        )

        aperturas = aperturas.filter(
            usuario=request.user
        )

        detalles = detalles.filter(
            venta__movimientocaja__apertura__usuario=request.user
        ).distinct()

    ventas_hoy = ventas.filter(
        created__date=hoy
    )

    movimientos_hoy = movimientos.filter(
        created__date=hoy
    )

    aperturas_hoy = aperturas.filter(
        fecha_apertura__date=hoy
    )

    ventas_dia = (
        ventas_hoy
        .filter(
            estado='PAGADA'
        )
        .aggregate(
            total=Sum('total')
        )['total']
        or
        0
    )

    devoluciones_dia = (
        ventas_hoy
        .filter(
            estado__in=[
                'ANULADA',
                'DEVUELTA'
            ]
        )
        .aggregate(
            total=Sum('total')
        )['total']
        or
        0
    )

    inicio_caja = (
        aperturas_hoy
        .aggregate(
            total=Sum('monto_inicial')
        )['total']
        or
        0
    )

    estado_caja = (
        inicio_caja
        + ventas_dia
        - devoluciones_dia
    )

    ventas_general = (
        ventas
        .filter(
            estado='PAGADA'
        )
        .aggregate(
            total=Sum('total')
        )['total']
        or
        0
    )

    devoluciones_general = (
        ventas
        .filter(
            estado__in=[
                'ANULADA',
                'DEVUELTA'
            ]
        )
        .aggregate(
            total=Sum('total')
        )['total']
        or
        0
    )

    ganancia_general = (
        ventas_general
        - devoluciones_general
    )

    numero_facturas_general = (
        ventas
        .filter(
            estado='PAGADA'
        )
        .count()
    )

    ventas_mensuales = []

    for mes in range(1, 13):

        total_mes = (
            ventas
            .filter(
                created__year=anio_actual,
                created__month=mes,
                estado='PAGADA'
            )
            .aggregate(
                total=Sum('total')
            )['total']
            or
            0
        )

        ventas_mensuales.append(
            decimal_float(
                total_mes
            )
        )

    ventas_mes_actual = (
        ventas
        .filter(
            created__year=anio_actual,
            created__month=mes_actual,
            estado='PAGADA'
        )
        .annotate(
            dia=TruncDate('created')
        )
        .values(
            'dia'
        )
        .annotate(
            total=Sum('total')
        )
        .order_by(
            'dia'
        )
    )

    dias_mes_labels = [
        item['dia'].strftime('%d/%m')
        for item in ventas_mes_actual
    ]

    dias_mes_data = [
        decimal_float(
            item['total']
        )
        for item in ventas_mes_actual
    ]

    productos_top = (
        detalles
        .filter(
            venta__estado='PAGADA'
        )
        .values(
            'producto__nombre'
        )
        .annotate(
            total_cantidad=Sum('cantidad'),
            total_vendido=Sum('subtotal')
        )
        .order_by(
            '-total_cantidad'
        )[:5]
    )

    productos_top_labels = [
        item['producto__nombre']
        for item in productos_top
    ]

    productos_top_data = [
        decimal_float(
            item['total_vendido']
        )
        for item in productos_top
    ]

    ventas_por_sede = (
        ventas
        .filter(
            estado='PAGADA'
        )
        .values(
            'sede__nombre'
        )
        .annotate(
            total=Sum('total')
        )
        .order_by(
            '-total'
        )
    )

    ventas_sede_labels = [
        item['sede__nombre']
        or
        'Sin sede'
        for item in ventas_por_sede
    ]

    ventas_sede_data = [
        decimal_float(
            item['total']
        )
        for item in ventas_por_sede
    ]

    cajas_abiertas = aperturas.filter(
        estado='ABIERTA'
    ).select_related(
        'caja',
        'caja__sede',
        'usuario'
    )

    resumen_cajas = []

    for apertura in aperturas_hoy.select_related(
        'caja',
        'caja__sede',
        'usuario'
    ):

        ingresos = (
            apertura.movimientos
            .filter(
                tipo='INGRESO'
            )
            .aggregate(
                total=Sum('monto')
            )['total']
            or
            0
        )

        egresos = (
            apertura.movimientos
            .filter(
                tipo='SALIDA'
            )
            .aggregate(
                total=Sum('monto')
            )['total']
            or
            0
        )

        esperado = (
            apertura.monto_inicial
            + ingresos
            - egresos
        )

        resumen_cajas.append({
            'caja': apertura.caja.nombre,
            'sede': apertura.caja.sede.nombre,
            'vendedor': apertura.usuario.username,
            'turno': apertura.get_turno_display(),
            'monto_inicial': apertura.monto_inicial,
            'ingresos': ingresos,
            'egresos': egresos,
            'esperado': esperado,
            'estado': apertura.estado,
        })

    productos_bajo_stock_lista = Producto.objects.filter(
        stock__lte=5,
        activo=True
    ).select_related(
        'categoria'
    ).order_by(
        'stock'
    )[:10]

    productos_bajo_stock = Producto.objects.filter(
        stock__lte=5,
        activo=True
    ).count()

    context = {
        'numero_facturas': ventas_hoy.count(),
        'ventas_dia': ventas_dia,
        'devoluciones_dia': devoluciones_dia,
        'inicio_caja': inicio_caja,
        'estado_caja': estado_caja,

        'numero_facturas_general': numero_facturas_general,
        'ventas_general': ventas_general,
        'devoluciones_general': devoluciones_general,
        'ganancia_general': ganancia_general,

        'productos_bajo_stock': productos_bajo_stock,
        'productos_bajo_stock_lista': productos_bajo_stock_lista,

        'cajas_abiertas': cajas_abiertas,
        'resumen_cajas': resumen_cajas,

        'productos_top': productos_top,
        'productos_top_labels': productos_top_labels,
        'productos_top_data': productos_top_data,

        'ventas_mensuales': ventas_mensuales,
        'dias_mes_labels': dias_mes_labels,
        'dias_mes_data': dias_mes_data,

        'ventas_sede_labels': ventas_sede_labels,
        'ventas_sede_data': ventas_sede_data,

        'es_admin_o_super': es_admin,
    }

    return render(
        request,
        'core/home.html',
        context
    )