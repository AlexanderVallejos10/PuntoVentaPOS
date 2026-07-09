from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from clientes.models import Cliente
from usuarios.decorators import vendedor_required
from ventas.models import Venta


@vendedor_required
def cliente_detalle(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    ventas = Venta.objects.filter(
        cliente=cliente
    ).select_related(
        'cliente',
        'sede',
    ).order_by('-created')

    resumen_metodos = {}

    for venta in ventas:
        metodo = venta.get_metodo_pago_display() if hasattr(venta, 'get_metodo_pago_display') else venta.metodo_pago
        metodo = metodo or 'Efectivo'

        if metodo not in resumen_metodos:
            resumen_metodos[metodo] = {
                'total': Decimal('0.00'),
                'operaciones': 0,
            }

        resumen_metodos[metodo]['total'] += venta.total or Decimal('0.00')
        resumen_metodos[metodo]['operaciones'] += 1

    return render(
        request,
        'clientes/cliente_detalle.html',
        {
            'cliente': cliente,
            'ventas': ventas,
            'resumen_metodos': resumen_metodos,
        }
    )
