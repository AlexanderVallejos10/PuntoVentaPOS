from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from inventario.models import Sede
from inventario.models import StockBodega
from productos.models import Categoria
from usuarios.decorators import vendedor_required


@vendedor_required
def inventario_producto_list(request):
    sede_id = request.GET.get('sede', '')
    categoria_id = request.GET.get('categoria', '')
    buscar = request.GET.get('buscar', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 10))
    except (TypeError, ValueError):
        por_pagina = 10

    if por_pagina not in [10, 25, 50, 100]:
        por_pagina = 10

    sedes = Sede.objects.filter(activo=True).order_by('nombre')
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True
    )

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)

    if categoria_id:
        stocks = stocks.filter(producto__categoria_id=categoria_id)

    if buscar:
        stocks = stocks.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar)
        )

    stocks = stocks.order_by('producto__nombre', 'sede__nombre')

    paginator = Paginator(stocks, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(
        request,
        'inventario/inventario_producto_list.html',
        {
            'stocks': page_obj,
            'page_obj': page_obj,
            'paginator': paginator,
            'sedes': sedes,
            'categorias': categorias,
            'sede_id': sede_id,
            'categoria_id': categoria_id,
            'buscar': buscar,
            'por_pagina': por_pagina,
            'total_registros': paginator.count,
            'inicio_registro': page_obj.start_index(),
            'fin_registro': page_obj.end_index(),
            'querystring': query_params.urlencode(),
        }
    )
