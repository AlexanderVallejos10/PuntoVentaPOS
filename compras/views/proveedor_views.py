import json
import openpyxl

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from compras.models import Proveedor
from compras.services.proveedor_service import ProveedorService
from compras.services.documento_proveedor_service import DocumentoProveedorService
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


@administrador_required
def proveedor_list(request):
    buscar = request.GET.get('buscar', '')

    proveedores = Proveedor.objects.all()

    if buscar:
        proveedores = proveedores.filter(
            razon_social__icontains=buscar
        )

    proveedores = proveedores.order_by('razon_social')

    return render(
        request,
        'compras/proveedor_list.html',
        {
            'proveedores': proveedores,
            'buscar': buscar
        }
    )


@administrador_required
def proveedor_create(request):
    if request.method == 'POST':
        Proveedor.objects.create(
            tipo_documento=request.POST.get('tipo_documento'),
            numero_documento=request.POST.get('numero_documento'),
            razon_social=request.POST.get('razon_social'),
            telefono=request.POST.get('telefono'),
            email=request.POST.get('email'),
            direccion=request.POST.get('direccion'),
            activo=(request.POST.get('activo') == 'on')
        )

        messages.success(request, 'Proveedor registrado correctamente.')
        return redirect('compras:proveedor_list')

    return render(
        request,
        'compras/proveedor_form.html',
        {
            'titulo': 'Registrar proveedor'
        }
    )


@administrador_required
def proveedor_update(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    if request.method == 'POST':
        proveedor.tipo_documento  = request.POST.get('tipo_documento')
        proveedor.numero_documento = request.POST.get('numero_documento')
        proveedor.razon_social    = request.POST.get('razon_social')
        proveedor.telefono        = request.POST.get('telefono')
        proveedor.email           = request.POST.get('email')
        proveedor.direccion       = request.POST.get('direccion')
        proveedor.activo          = (request.POST.get('activo') == 'on')
        proveedor.save()

        messages.success(request, 'Proveedor actualizado correctamente.')
        return redirect('compras:proveedor_list')

    return render(
        request,
        'compras/proveedor_form.html',
        {
            'proveedor': proveedor,
            'titulo': 'Editar proveedor',
            'editar': True
        }
    )


@administrador_required
def proveedor_delete(request, proveedor_id):
    if request.method == 'POST':
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        proveedor.delete()
        return JsonResponse({'ok': True})

    return JsonResponse({'ok': False})


@administrador_required
def exportar_proveedores_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Proveedores'

    sheet.append([
        'Item',
        'Proveedor',
        'Tipo Doc',
        'Documento',
        'Teléfono',
        'Correo',
        'Dirección',
        'Estado'
    ])

    proveedores = Proveedor.objects.all().order_by('razon_social')

    for i, proveedor in enumerate(proveedores, start=1):
        sheet.append([
            i,
            proveedor.razon_social,
            proveedor.tipo_documento,
            proveedor.numero_documento,
            proveedor.telefono or '-',
            proveedor.email or '-',
            proveedor.direccion or '-',
            'Activo' if proveedor.activo else 'Inactivo'
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=proveedores.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_proveedores_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=proveedores.pdf'

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
        'Lista de Proveedores'
    )

    data = [[
        'Item',
        'Proveedor',
        'Documento',
        'Teléfono',
        'Correo',
    ]]

    proveedores = Proveedor.objects.all().order_by('razon_social')

    for i, proveedor in enumerate(proveedores, start=1):
        data.append([
            str(i),
            str(proveedor.razon_social),
            str(proveedor.numero_documento),
            str(proveedor.telefono or '-'),
            str(proveedor.email or '-'),
        ])

    tabla = Table(
        data,
        colWidths=[35, 160, 100, 90, 130]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response


@administrador_required
def consultar_documento_proveedor_ajax(request):
    tipo   = request.GET.get('tipo', '').upper()
    numero = request.GET.get('numero', '').strip()

    if tipo == 'DNI':
        resultado = DocumentoProveedorService.buscar_dni(numero)
    elif tipo == 'RUC':
        resultado = DocumentoProveedorService.buscar_ruc(numero)
    else:
        resultado = {'ok': False}

    return JsonResponse(resultado)


@administrador_required
def crear_proveedor_ajax(request):
    data      = json.loads(request.body)
    proveedor = ProveedorService.crear_proveedor(data)

    return JsonResponse({
        'ok':     True,
        'id':     proveedor.id,
        'nombre': proveedor.razon_social
    })