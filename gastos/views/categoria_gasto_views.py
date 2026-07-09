from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from gastos.models.categoria_gasto import CategoriaGasto
from gastos.forms.categoria_gasto_form import CategoriaGastoForm
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa


def categoria_gasto_list(request):
    buscar = request.GET.get('buscar', '').strip()
    editar_id = request.GET.get('editar')
    nueva = request.GET.get('nuevo')

    categorias = CategoriaGasto.objects.all().order_by('nombre')

    if buscar:
        categorias = categorias.filter(nombre__icontains=buscar)

    form = None
    categoria_editar = None

    if editar_id:
        categoria_editar = get_object_or_404(CategoriaGasto, id=editar_id)
        form = CategoriaGastoForm(instance=categoria_editar)

    elif nueva:
        form = CategoriaGastoForm()

    return render(
        request,
        'gastos/categoria_gasto_list.html',
        {
            'categorias': categorias,
            'buscar': buscar,
            'form': form,
            'categoria_editar': categoria_editar,
            'mostrar_modal': True if form else False,
        }
    )


def categoria_gasto_save(request):
    categoria_id = request.POST.get('categoria_id')

    if categoria_id:
        categoria = get_object_or_404(CategoriaGasto, id=categoria_id)
        form = CategoriaGastoForm(request.POST, instance=categoria)
    else:
        form = CategoriaGastoForm(request.POST)

    if form.is_valid():
        form.save()

    return redirect('gastos:categoria_gasto_list')


def categoria_gasto_delete(request, pk):
    categoria = get_object_or_404(CategoriaGasto, pk=pk)
    categoria.delete()

    return redirect('gastos:categoria_gasto_list')


def categoria_gasto_excel(request):
    categorias = CategoriaGasto.objects.all().order_by('nombre')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Categorias Gastos'

    hoja.append([
        'Item',
        'Nombre',
        'Estado',
    ])

    for index, categoria in enumerate(categorias, start=1):
        hoja.append([
            index,
            categoria.nombre,
            'ACTIVO' if categoria.activo else 'INACTIVO',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=categorias_gastos.xlsx'

    workbook.save(response)
    return response


def categoria_gasto_pdf(request):
    categorias = CategoriaGasto.objects.all().order_by('nombre')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=categorias_gastos.pdf'

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
        'Categorías de Gastos'
    )

    data = [[
        'Item',
        'Nombre',
        'Estado'
    ]]

    for index, categoria in enumerate(categorias, start=1):
        data.append([
            str(index),
            categoria.nombre,
            'ACTIVO' if categoria.activo else 'INACTIVO'
        ])

    tabla = Table(
        data,
        colWidths=[50, 300, 100]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response