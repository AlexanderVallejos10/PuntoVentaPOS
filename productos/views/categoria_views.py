from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from productos.forms import CategoriaForm
from productos.models import Categoria
from django.contrib.auth.decorators import login_required

from usuarios.decorators import vendedor_required


@login_required
def categoria_create(request):
    form = CategoriaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Categoría creada correctamente.'
            )

            return redirect('inventario:categoria_inventario_list')

    return render(
        request,
        'productos/categoria_form.html',
        {
            'form': form,
            'titulo': 'Nueva Categoría'
        }
    )


@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(
        Categoria,
        pk=pk
    )

    form = CategoriaForm(
        request.POST or None,
        instance=categoria
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Categoría actualizada correctamente.'
            )

            return redirect('inventario:categoria_inventario_list')

    return render(
        request,
        'productos/categoria_form.html',
        {
            'form': form,
            'titulo': 'Editar Categoría'
        }
    )


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(
        Categoria,
        pk=pk
    )

    categoria.delete()

    messages.success(
        request,
        'Categoría eliminada correctamente.'
    )

    return redirect('inventario:categoria_inventario_list')