from collections import defaultdict

import openpyxl

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from gastos.models.gasto import Gasto
from gastos.models.categoria_gasto import CategoriaGasto
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa


def gasto_categoria_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin    = request.GET.get('fecha_fin', '')
    categoria_id = request.GET.get('categoria', '')
    tipo_gasto   = request.GET.get('tipo_gasto', '')
    usuario_id   = request.GET.get('usuario', '')

    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    if fecha_inicio:
        gastos = gastos.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        gastos = gastos.filter(fecha__date__lte=fecha_fin)

    if categoria_id:
        gastos = gastos.filter(categoria_id=categoria_id)

    if tipo_gasto:
        gastos = gastos.filter(tipo_gasto=tipo_gasto)

    if usuario_id:
        gastos = gastos.filter(responsable_id=usuario_id)

    grupos_dict = defaultdict(list)

    for gasto in gastos:
        grupos_dict[gasto.categoria.nombre].append(gasto)

    grupos = []

    for categoria, lista_gastos in grupos_dict.items():
        total   = sum(g.valor for g in lista_gastos)
        contado = sum(g.valor for g in lista_gastos if g.sacar_caja)
        credito = sum(g.valor for g in lista_gastos if not g.sacar_caja)
        grupos.append({
            'categoria': categoria,
            'gastos':    lista_gastos,
            'total':     total,
            'contado':   contado,
            'credito':   credito,
        })

    User = get_user_model()

    return render(
        request,
        'gastos/gasto_categoria_list.html',
        {
            'grupos':      grupos,
            'categorias':  CategoriaGasto.objects.all().order_by('nombre'),
            'usuarios':    User.objects.filter(is_active=True).order_by('username'),
            'fecha_inicio': fecha_inicio,
            'fecha_fin':    fecha_fin,
            'categoria_id': categoria_id,
            'tipo_gasto':   tipo_gasto,
            'usuario_id':   usuario_id,
        }
    )


def gasto_categoria_excel(request):
    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Gastos por categoria'

    hoja.append([
        'Item',
        'Fecha y Hora',
        'Descripción',
        'Categoría',
        'Tipo',
        'Proveedor',
        'Responsable',
        'Método de pago',
        'Valor',
        'Abonado',
        'Saldo',
        'Egreso de caja',
        'Estado',
    ])

    for index, gasto in enumerate(gastos, start=1):
        hoja.append([
            index,
            gasto.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            gasto.descripcion,
            gasto.categoria.nombre,
            gasto.tipo_gasto,
            gasto.proveedor.razon_social if gasto.proveedor else '-',
            gasto.responsable.username if gasto.responsable else '-',
            gasto.metodo_pago,
            float(gasto.valor),
            float(gasto.valor) if gasto.tipo_gasto == 'CONTADO' else 0,
            0 if gasto.tipo_gasto == 'CONTADO' else float(gasto.valor),
            'SI' if gasto.sacar_caja else 'NO',
            gasto.estado,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=gastos_por_categoria.xlsx'

    workbook.save(response)
    return response


def gasto_categoria_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=gastos_por_categoria.pdf'

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
        'Gastos por Categoría'
    )

    data = [[
        'Item',
        'Fecha',
        'Descripción',
        'Categoría',
        'Valor',
        'Tipo',
        'Estado',
    ]]

    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    for index, gasto in enumerate(gastos, start=1):
        data.append([
            str(index),
            gasto.fecha.strftime('%Y-%m-%d'),
            str(gasto.descripcion)[:30],
            str(gasto.categoria.nombre)[:18],
            f'S/ {gasto.valor}',
            gasto.tipo_gasto,
            gasto.estado,
        ])

    tabla = Table(
        data,
        colWidths=[30, 70, 140, 90, 60, 60, 55]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response