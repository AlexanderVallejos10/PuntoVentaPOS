import openpyxl

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from clientes.models import Cliente
from ventas.models import Venta


def exportar_detalle_cliente_excel(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    ventas = Venta.objects.filter(
        cliente=cliente
    ).order_by('-created')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Historial cliente'

    hoja.append(['Cliente', cliente.nombre])
    hoja.append([])
    hoja.append([
        'Comprobante',
        'Fecha y hora',
        'Método pago',
        'Total',
        'Estado',
    ])

    for venta in ventas:
        hoja.append([
            venta.comprobante_codigo,
            venta.created.strftime('%Y-%m-%d %H:%M:%S'),
            venta.metodo_pago or 'EFECTIVO',
            float(venta.total),
            venta.estado,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_cliente.xlsx'

    workbook.save(response)
    return response
