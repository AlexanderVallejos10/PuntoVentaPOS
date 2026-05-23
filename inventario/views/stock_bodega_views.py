from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from inventario.forms import StockBodegaForm
from inventario.models import StockBodega
from productos.models import Producto
from usuarios.decorators import vendedor_required


def generar_codigo_producto():
    ultimo = Producto.objects.order_by('id').last()

    if not ultimo:
        numero = 1
    else:
        numero = ultimo.id + 1

    return f'PROD-{numero:06d}'


@vendedor_required
def stock_bodega_create(request):
    form = StockBodegaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            sede = form.cleaned_data['sede']

            producto = Producto.objects.create(
                codigo=generar_codigo_producto(),
                nombre=nombre,
                categoria=form.cleaned_data['categoria'],
                descripcion=form.cleaned_data['descripcion'],
                precio_compra=form.cleaned_data['precio_compra'] or 0,
                precio_venta=form.cleaned_data['precio_venta'],
                imagen_url=form.cleaned_data['imagen_url'],
                activo=form.cleaned_data['activo']
            )

            StockBodega.objects.create(
                sede=sede,
                producto=producto,
                stock=form.cleaned_data['stock'],
                stock_minimo=form.cleaned_data['stock_minimo'],
                activo=form.cleaned_data['activo']
            )

            messages.success(
                request,
                'Producto creado y asignado a bodega correctamente.'
            )

            return redirect('inventario:inventario_producto_list')

    return render(
        request,
        'inventario/stock_bodega_form.html',
        {
            'form': form,
            'titulo': 'Nuevo producto'
        }
    )


@vendedor_required
def stock_bodega_update(request, pk):
    stock_bodega = get_object_or_404(
        StockBodega,
        pk=pk
    )

    producto = stock_bodega.producto

    initial = {
        'nombre': producto.nombre,
        'categoria': producto.categoria,
        'descripcion': producto.descripcion,
        'precio_compra': producto.precio_compra,
        'precio_venta': producto.precio_venta,
        'imagen_url': producto.imagen_url,
    }

    form = StockBodegaForm(
        request.POST or None,
        instance=stock_bodega,
        initial=initial
    )

    if request.method == 'POST':
        if form.is_valid():
            producto.nombre = form.cleaned_data['nombre']
            producto.categoria = form.cleaned_data['categoria']
            producto.descripcion = form.cleaned_data['descripcion']
            producto.precio_compra = form.cleaned_data['precio_compra'] or 0
            producto.precio_venta = form.cleaned_data['precio_venta']
            producto.imagen_url = form.cleaned_data['imagen_url']
            producto.activo = form.cleaned_data['activo']
            producto.save()

            stock_bodega.sede = form.cleaned_data['sede']
            stock_bodega.stock = form.cleaned_data['stock']
            stock_bodega.stock_minimo = form.cleaned_data['stock_minimo']
            stock_bodega.activo = form.cleaned_data['activo']
            stock_bodega.save()

            messages.success(
                request,
                'Producto e inventario actualizados correctamente.'
            )

            return redirect('inventario:inventario_producto_list')

    return render(
        request,
        'inventario/stock_bodega_form.html',
        {
            'form': form,
            'titulo': 'Editar producto'
        }
    )

@vendedor_required
def stock_bodega_delete(request, pk):
    stock_bodega = get_object_or_404(
        StockBodega,
        pk=pk
    )

    producto = stock_bodega.producto

    stock_bodega.delete()
    producto.delete()

    messages.success(
        request,
        'Producto eliminado correctamente.'
    )

    return redirect('inventario:inventario_producto_list')