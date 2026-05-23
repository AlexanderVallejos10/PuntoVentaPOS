from django.urls import path

from productos.views.producto_views import imprimir_barcode_producto, producto_list
from productos.views.producto_views import producto_create
from productos.views.producto_views import producto_update
from productos.views.producto_views import producto_delete
from productos.views.producto_views import producto_label
from productos.views.categoria_views import categoria_create
from productos.views.categoria_views import categoria_update
from productos.views.categoria_views import categoria_delete

app_name = 'productos'

urlpatterns = [
    path('', producto_list, name='producto_list'),
    path('crear/', producto_create, name='producto_create'),
    path('editar/<int:pk>/', producto_update, name='producto_update'),
    path('eliminar/<int:pk>/', producto_delete, name='producto_delete'),
    path('etiqueta/<int:pk>/', producto_label, name='producto_label'),
    path('categorias/nueva/',categoria_create,name='categoria_create'),
    path('categorias/editar/<int:pk>/',categoria_update,name='categoria_update'),
    path('categorias/eliminar/<int:pk>/',categoria_delete,name='categoria_delete'),
    path('productos/<int:producto_id>/barcode/',imprimir_barcode_producto,name='imprimir_barcode_producto'),
]