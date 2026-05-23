from django.shortcuts import render

from productos.models import Categoria
from django.contrib.auth.decorators import login_required

@login_required
def categoria_inventario_list(request):
    buscar = request.GET.get('buscar', '').strip()

    categorias = Categoria.objects.all().order_by('id')

    if buscar:
        categorias = categorias.filter(nombre__icontains=buscar)

    return render(
        request,
        'inventario/categoria_inventario_list.html',
        {
            'categorias': categorias,
            'buscar': buscar,
        }
    )