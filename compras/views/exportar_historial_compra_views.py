import openpyxl

from django.db.models import Q
from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from compras.models import Compra
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


def obtener_compras_filtradas(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    estado = request.GET.get('estado', '')
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    compras = Compra.objects.select_related(
        'proveedor',
        'sede',
        'responsable'
    ).all()

    if fecha_inicio:
        compras = compras.filter(fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        compras = compras.filter(fecha_compra__date__lte=fecha_fin)

    if estado:
        compras = compras.filter(estado=estado)

    if sede_id:
        compras = compras.filter(sede_id=sede_id)

    if buscar:
        compras = compras.filter(
            Q(codigo__icontains=buscar) |
            Q(numero_comprobante__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar) |
            Q(proveedor__numero_documento__icontains=buscar)
        )

    return compras.order_by('-fecha_compra')


@administrador_required
def exportar_historial_compras_excel(request):
    compras = obtener_compras_filtradas(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Historial compras'

    hoja.append([
        'Item',
        'Factura',
        'Bodega',
        'Factura proveedor',
        'Fecha y hora',
        'Proveedor',
        'Atendió',
        'Método de pago',
        'Valor compra',
        'Salió de caja',
        'Estado',
    ])

    total = 0

    for index, compra in enumerate(compras, start=1):
        total += compra.total

        hoja.append([
            index,
            compra.codigo,
            compra.sede.nombre,
            compra.numero_comprobante or '',
            compra.fecha_compra.strftime('%d/%m/%Y %H:%M'),
            compra.proveedor.razon_social,
            compra.responsable.username if compra.responsable else '',
            'EFECTIVO',
            float(compra.total),
            'SI',
            compra.estado,
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', '', '', 'TOTAL', float(total)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_compras.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_historial_compras_pdf(request):
    compras = obtener_compras_filtradas(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=historial_compras.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    elementos = []

    # Cabecera dinámica con logo y datos de empresa
    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Historial de Compras'
    )

    elementos.append(Spacer(1, 12))

    data = [[
        'Item',
        'Factura',
        'Bodega',
        'Proveedor',
        'Fecha',
        'Atendió',
        'Total',
        'Estado'
    ]]

    total = 0

    for index, compra in enumerate(compras, start=1):
        total += compra.total

        data.append([
            str(index),
            compra.codigo[:12],
            compra.sede.nombre[:14],
            compra.proveedor.razon_social[:25],
            compra.fecha_compra.strftime('%d/%m/%Y'),
            compra.responsable.username if compra.responsable else '-',
            f'S/ {compra.total:.2f}',
            compra.estado
        ])

    tabla = Table(
        data,
        colWidths=[40, 70, 75, 100, 75, 70, 70, 70]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (6, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 12))

    # Totales
    totales_data = [
        ['', '', '', '', '', 'TOTAL:', f'S/ {total:.2f}', '']
    ]

    totales_tabla = Table(totales_data, colWidths=[40, 70, 75, 100, 75, 70, 70, 70])
    totales_tabla.setStyle(TableStyle([
        ('FONTNAME',  (5, 0), (6, 0), 'Helvetica-Bold'),
        ('FONTSIZE',  (5, 0), (6, 0), 9),
        ('ALIGN',     (5, 0), (6, 0), 'RIGHT'),
    ]))

    elementos.append(totales_tabla)

    doc.build(elementos)

    return response