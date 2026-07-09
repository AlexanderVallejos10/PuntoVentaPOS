import openpyxl

from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from clientes.models import Cliente
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


@administrador_required
def exportar_clientes_excel(request):
    clientes = Cliente.objects.all().order_by('nombre')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Clientes'

    hoja.append([
        'Item',
        'Nombre / razón social',
        'Tipo documento',
        'Número documento',
        'Teléfono',
        'Correo',
        'Dirección',
        'Estado',
    ])

    for index, cliente in enumerate(clientes, start=1):
        hoja.append([
            index,
            cliente.nombre,
            cliente.tipo_documento,
            cliente.numero_documento or '',
            cliente.telefono or '',
            cliente.email or '',
            cliente.direccion or '',
            'Activo' if cliente.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_clientes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=clientes.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30,
    )

    elementos = []
    empresa = ConfiguracionEmpresa.obtener_configuracion()
    agregar_cabecera_empresa(elementos, empresa, 'Lista de clientes')

    data = [[
        'Item',
        'Nombre',
        'Documento',
        'Teléfono',
        'Correo',
    ]]

    for index, cliente in enumerate(Cliente.objects.all().order_by('nombre'), start=1):
        data.append([
            str(index),
            str(cliente.nombre),
            str(cliente.numero_documento or '-'),
            str(cliente.telefono or '-'),
            str(cliente.email or '-'),
        ])

    tabla = Table(data, colWidths=[35, 160, 100, 90, 130])
    tabla.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    return response
