import openpyxl

from django.http import HttpResponse
from django.shortcuts import render

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from inventario.models import ConfiguracionEmpresa, StockBodega
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import vendedor_required


def obtener_stocks_exportar():
    return StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True
    ).order_by(
        'producto__nombre'
    )


@vendedor_required
def preview_exportar_productos(request):
    stocks = obtener_stocks_exportar()

    return render(
        request,
        'inventario/preview_exportar_productos.html',
        {
            'stocks': stocks
        }
    )


@vendedor_required
def exportar_productos_excel(request):
    stocks = obtener_stocks_exportar()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Productos'

    hoja.append([
        'Item',
        'Código',
        'Nombre',
        'Categoría',
        'Bodega',
        'Stock',
        'Compra',
        'Venta',
        'Estado',
    ])

    for index, stock in enumerate(stocks, start=1):
        hoja.append([
            index,
            stock.producto.codigo,
            stock.producto.nombre,
            stock.producto.categoria.nombre if stock.producto.categoria else '',
            stock.sede.nombre if stock.sede else '',
            float(stock.stock),
            float(stock.producto.precio_compra),
            float(stock.producto.precio_venta),
            'Activo' if stock.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=productos_inventario.xlsx'

    workbook.save(response)

    return response


@vendedor_required
def exportar_productos_pdf(request):
    stocks = obtener_stocks_exportar()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=productos_inventario.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    elementos = []

    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Productos de Inventario'
    )

    data = [[
        'Item',
        'Código',
        'Nombre',
        'Bodega',
        'Stock',
        'Venta',
    ]]

    for index, stock in enumerate(stocks, start=1):
        data.append([
            str(index),
            stock.producto.codigo,
            stock.producto.nombre,
            stock.sede.nombre if stock.sede else '-',
            str(stock.stock),
            f'S/ {stock.producto.precio_venta}',
        ])

    tabla = Table(
        data,
        colWidths=[30, 70, 190, 110, 50, 65]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response