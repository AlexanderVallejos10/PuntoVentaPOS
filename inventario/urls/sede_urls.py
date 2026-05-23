from django.urls import path
from inventario.views.sede_views import sede_create
from inventario.views.sede_views import sede_delete
from inventario.views.sede_views import sede_list
from inventario.views.sede_views import sede_update
from inventario.views.inventario_producto_views import inventario_producto_list
from inventario.views.stock_bodega_views import stock_bodega_create
from inventario.views.stock_bodega_views import stock_bodega_update
from inventario.views.menu_digital_views import menu_digital_productos
from inventario.views.variacion_producto_views import variacion_producto_list
from inventario.views.importar_productos_views import importar_productos_excel
from inventario.views.importar_productos_views import descargar_formato_productos
from inventario.views.stock_bodega_views import stock_bodega_delete
from inventario.views.actualizar_productos_views import actualizar_productos_excel
from inventario.views.exportar_productos_views import preview_exportar_productos
from inventario.views.exportar_productos_views import exportar_productos_excel
from inventario.views.exportar_productos_views import exportar_productos_pdf
from inventario.views.categoria_inventario_views import categoria_inventario_list
from inventario.views.importar_exportar_categorias_views import importar_categorias_excel
from inventario.views.importar_exportar_categorias_views import descargar_formato_categorias
from inventario.views.importar_exportar_categorias_views import exportar_categorias_excel
from inventario.views.importar_exportar_categorias_views import exportar_categorias_pdf
from inventario.views.baja_existencia_views import baja_existencia_list
from inventario.views.estado_inventario_views import estado_inventario
from inventario.views.exportar_inventario_views import exportar_baja_existencia_excel
from inventario.views.exportar_inventario_views import exportar_baja_existencia_pdf
from inventario.views.exportar_inventario_views import exportar_estado_inventario_excel
from inventario.views.exportar_inventario_views import exportar_estado_inventario_pdf
from inventario.views.traslado_views import traslado_list
from inventario.views.traslado_views import traslado_create
from inventario.views.exportar_traslado_views import exportar_traslado_excel
from inventario.views.exportar_traslado_views import exportar_traslado_pdf
from inventario.views.importar_traslado_views import importar_traslados_excel
from inventario.views.importar_traslado_views import descargar_formato_traslados
from inventario.views.inventario_categoria_views import inventario_categoria_list
from inventario.views.exportar_inventario_categoria_views import exportar_inventario_categoria_excel
from inventario.views.exportar_inventario_categoria_views import exportar_inventario_categoria_pdf
from inventario.views.promocion_views import promocion_list
from inventario.views.promocion_views import promocion_create
from inventario.views.promocion_views import promocion_update
from inventario.views.exportar_promocion_views import exportar_promociones_excel
from inventario.views.exportar_promocion_views import exportar_promociones_pdf
from inventario.views.seguimiento_producto_views import seguimiento_producto_list
from inventario.views.exportar_seguimiento_views import exportar_seguimiento_excel
from inventario.views.exportar_seguimiento_views import exportar_seguimiento_pdf
from inventario.views.configuracion_empresa_views import configuracion_empresa
from productos.views.producto_views import imprimir_barcode_producto

app_name = 'inventario'

urlpatterns = [
    path('bodegas/', sede_list, name='sede_list'),
    path('bodegas/nueva/', sede_create, name='sede_create'),
    path('bodegas/editar/<int:pk>/', sede_update, name='sede_update'),
    path('bodegas/eliminar/<int:pk>/', sede_delete, name='sede_delete'),
    path('productos/', inventario_producto_list, name='inventario_producto_list'),
    path('ajustes/nuevo/', stock_bodega_create, name='stock_bodega_create'),
    path('ajustes/editar/<int:pk>/', stock_bodega_update, name='stock_bodega_update'),
    path('productos/menu-digital/', menu_digital_productos, name='menu_digital_productos'),
    path('productos/variaciones/', variacion_producto_list, name='variacion_producto_list'),
    path('productos/importar/',importar_productos_excel,name='importar_productos_excel'),
    path('productos/importar/',importar_productos_excel,name='importar_productos_excel'),
    path('productos/importar/formato/',descargar_formato_productos,name='descargar_formato_productos'),
    path('ajustes/eliminar/<int:pk>/',stock_bodega_delete,name='stock_bodega_delete'),
    path('productos/actualizar/',actualizar_productos_excel,name='actualizar_productos_excel'),
    path('productos/exportar/preview/',preview_exportar_productos,name='preview_exportar_productos'),
    path('productos/exportar/excel/',exportar_productos_excel,name='exportar_productos_excel'),
    path('productos/exportar/pdf/',exportar_productos_pdf,name='exportar_productos_pdf'),
    path('categorias/',categoria_inventario_list,name='categoria_inventario_list'),
    path('categorias/importar/',importar_categorias_excel,name='importar_categorias_excel'),
    path('categorias/importar/formato/',descargar_formato_categorias,name='descargar_formato_categorias'),
    path('categorias/exportar/excel/',exportar_categorias_excel,name='exportar_categorias_excel'),
    path('categorias/exportar/pdf/',exportar_categorias_pdf,name='exportar_categorias_pdf'),
    path('baja-existencia/',baja_existencia_list,name='baja_existencia_list'),
    path('estado/',estado_inventario,name='estado_inventario'),
    path('baja-existencia/exportar/excel/',exportar_baja_existencia_excel,name='exportar_baja_existencia_excel'),
    path('baja-existencia/exportar/pdf/',exportar_baja_existencia_pdf,name='exportar_baja_existencia_pdf'),
    path('estado/exportar/excel/',exportar_estado_inventario_excel,name='exportar_estado_inventario_excel'),
    path('estado/exportar/pdf/',exportar_estado_inventario_pdf,name='exportar_estado_inventario_pdf'),
    path('traslados/',traslado_list,name='traslado_list'),
    path('traslados/nuevo/',traslado_create,name='traslado_create'),
    path('traslados/exportar/excel/',exportar_traslado_excel,name='exportar_traslado_excel'),
    path('traslados/exportar/pdf/',exportar_traslado_pdf,name='exportar_traslado_pdf'),
    path('traslados/importar/',importar_traslados_excel,name='importar_traslados_excel'),
    path('traslados/importar/formato/',descargar_formato_traslados,name='descargar_formato_traslados'),
    path('inventario-categorias/',inventario_categoria_list,name='inventario_categoria_list'),
    path('inventario-categorias/exportar/excel/',exportar_inventario_categoria_excel,name='exportar_inventario_categoria_excel'),
    path('inventario-categorias/exportar/pdf/',exportar_inventario_categoria_pdf,name='exportar_inventario_categoria_pdf'),
    path('promociones/',promocion_list,name='promocion_list'),
    path('promociones/nueva/',promocion_create,name='promocion_create'),
    path('promociones/editar/<int:pk>/',promocion_update,name='promocion_update'),
    path('promociones/exportar/excel/',exportar_promociones_excel,name='exportar_promociones_excel'),
    path('promociones/exportar/pdf/',exportar_promociones_pdf,name='exportar_promociones_pdf'),
    path('seguimiento-productos/',seguimiento_producto_list,name='seguimiento_producto_list'),
    path('seguimiento-productos/exportar/excel/',exportar_seguimiento_excel,name='exportar_seguimiento_excel'),
    path('seguimiento-productos/exportar/pdf/',exportar_seguimiento_pdf,name='exportar_seguimiento_pdf'),
    path('configuracion/',configuracion_empresa,name='configuracion_empresa'),
    path('productos/imprimir-codigo/<int:producto_id>/',imprimir_barcode_producto,name='imprimir_barcode_producto'),
]