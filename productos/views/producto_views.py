from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from productos.forms import ProductoForm
from productos.models import Producto
from productos.services.producto_service import ProductoService
from productos.services.barcode_service import BarcodeService
from django.contrib.auth.decorators import login_required


@login_required
def producto_list(request):
    productos = Producto.objects.select_related('categoria').all()

    return render(
        request,
        'productos/producto_list.html',
        {
            'productos': productos
        }
    )


@login_required
def producto_create(request):
    form = ProductoForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            producto = form.save(commit=False)

            if not producto.codigo:
                producto.codigo = ProductoService.generar_codigo_producto()

            producto.save()

            if not producto.barcode_image:
                producto.barcode_image = BarcodeService.generar_codigo_barras(
                    producto.codigo
                )
                producto.save()

            messages.success(
                request,
                'Producto guardado correctamente.'
            )

            return redirect('productos:producto_list')

    return render(
        request,
        'productos/producto_form.html',
        {
            'form': form,
            'titulo': 'Nuevo producto'
        }
    )


@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    form = ProductoForm(
        request.POST or None,
        request.FILES or None,
        instance=producto
    )

    if request.method == 'POST':
        if form.is_valid():
            producto = form.save()

            if not producto.barcode_image:
                producto.barcode_image = BarcodeService.generar_codigo_barras(
                    producto.codigo
                )
                producto.save()

            messages.success(
                request,
                'Producto guardado correctamente.'
            )

            return redirect('productos:producto_list')

    return render(
        request,
        'productos/producto_form.html',
        {
            'form': form,
            'titulo': 'Editar producto'
        }
    )


@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.delete()
        return redirect('productos:producto_list')

    return render(
        request,
        'productos/producto_confirm_delete.html',
        {
            'producto': producto
        }
    )


@login_required
def producto_label(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    return render(
        request,
        'productos/producto_label.html',
        {
            'producto': producto,
            'now': timezone.now()
        }
    )


@login_required
def imprimir_barcode_producto(request, producto_id):
    producto = get_object_or_404(
        Producto,
        id=producto_id
    )

    if not producto.barcode_image:
        producto.barcode_image = BarcodeService.generar_codigo_barras(
            producto.codigo
        )
        producto.save()

    return render(
        request,
        'productos/imprimir_barcode.html',
        {
            'producto': producto
        }
    )