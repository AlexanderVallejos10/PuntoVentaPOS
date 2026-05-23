from decimal import Decimal

from django.shortcuts import render
from django.db.models import Q
from inventario.models import Sede
from inventario.models import StockBodega
from django.contrib.auth.decorators import login_required

@login_required
def estado_inventario(request):
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    )

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)

    if buscar:
        stocks = stocks.filter(Q(producto__nombre__icontains=buscar) | Q(producto__codigo__icontains=buscar))

    stocks = stocks.order_by('producto__nombre')

    costo_total = Decimal('0.00')
    venta_total = Decimal('0.00')

    for item in stocks:
        item.total_costo = item.stock * item.producto.precio_compra
        item.total_venta = item.stock * item.producto.precio_venta

        costo_total += item.total_costo
        venta_total += item.total_venta

    return render(
        request,
        'inventario/estado_inventario.html',
        {
            'stocks': stocks,
            'sedes': sedes,
            'sede_id': sede_id,
            'buscar': buscar,
            'costo_total': costo_total,
            'venta_total': venta_total,
        }
    )