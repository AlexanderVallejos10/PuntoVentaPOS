from django.urls import path

from ventas.views.pos_views import pos_venta
from ventas.views.pos_views import agregar_producto_scanner
from ventas.views.pos_views import quitar_producto_carrito
from ventas.views.pos_views import limpiar_carrito
from ventas.views.pos_views import confirmar_venta
from ventas.views.pos_views import ticket_venta
from ventas.views.pos_views import aumentar_cantidad
from ventas.views.pos_views import disminuir_cantidad
from ventas.views.pos_views import guardar_venta_espera
from ventas.views.pos_views import cargar_venta_espera
from ventas.views.pos_views import eliminar_venta_espera
from ventas.views.pos_views import seleccionar_sede_pos
from ventas.views.pos_views import resumen_venta
from ventas.views.pos_views import (imprimir_ticket, imprimir_carta, enviar_factura_correo,)
from ventas.views.pos_views import historial_ventas
from ventas.views.pos_views import eliminar_venta_ajax
from ventas.views.caja_views import abrir_caja
from ventas.views.caja_views import cerrar_caja
from ventas.views.caja_admin_views import *
from ventas.views.pos_views import devolver_venta_ajax
from ventas.views.pos_views import editar_venta
from ventas.views.pos_views import exportar_historial_ventas_excel
from ventas.views.pos_views import exportar_historial_ventas_pdf
from ventas.views.pos_views import detalle_ventas
from ventas.views.pos_views import ventas_por_categoria
from ventas.views.pos_views import exportar_detalle_ventas_excel
from ventas.views.pos_views import exportar_detalle_ventas_pdf
from ventas.views.pos_views import exportar_ventas_categoria_excel
from ventas.views.pos_views import exportar_ventas_categoria_pdf

app_name = 'ventas'

urlpatterns = [
    path('', pos_venta, name='pos_venta'),
    path('agregar/', agregar_producto_scanner, name='agregar_producto_scanner'),
    path('quitar/<int:producto_id>/', quitar_producto_carrito, name='quitar_producto_carrito'),
    path('limpiar/', limpiar_carrito, name='limpiar_carrito'),
    path('confirmar/', confirmar_venta, name='confirmar_venta'),
    path('ticket/<int:venta_id>/', ticket_venta, name='ticket_venta'),
    path('aumentar/<int:producto_id>/', aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir/<int:producto_id>/', disminuir_cantidad, name='disminuir_cantidad'),
    path('guardar_espera/', guardar_venta_espera, name='guardar_venta_espera'),
    path('guardar-espera/',guardar_venta_espera, name='guardar_venta_espera'),
    path('espera/<int:venta_id>/eliminar/',eliminar_venta_espera,name='eliminar_venta_espera'),
    path('espera/<int:venta_id>/cargar/', cargar_venta_espera, name='cargar_venta_espera'),
    path('seleccionar-sede/',seleccionar_sede_pos, name='seleccionar_sede_pos'),
    path('resumen/<int:venta_id>/',resumen_venta,name='resumen_venta'),
    path('imprimir-ticket/<int:venta_id>/',imprimir_ticket, name='imprimir_ticket'),
    path('imprimir-carta/<int:venta_id>/',imprimir_carta,name='imprimir_carta'),
    path('enviar-factura-correo/<int:venta_id>/',enviar_factura_correo,name='enviar_factura_correo'),
    path('historial/',historial_ventas,name='historial_ventas'),
    path('historial/eliminar/<int:venta_id>/',eliminar_venta_ajax,name='eliminar_venta_ajax'),
    path('caja/abrir/',abrir_caja,name='abrir_caja'),
    path('caja/cerrar/',cerrar_caja,name='cerrar_caja'),
    path('caja/list/',caja_list,name='caja_list'),
    path('caja/create/',caja_create,name='caja_create'),
    path('caja/update/<int:caja_id>/',caja_update,name='caja_update'),
    path('caja/delete/<int:caja_id>/',caja_delete,name='caja_delete'),
    path('historial/devolver/<int:venta_id>/',devolver_venta_ajax,name='devolver_venta_ajax'), 
    path('historial/eliminar/<int:venta_id>/',eliminar_venta_ajax,name='eliminar_venta_ajax'),
    path('historial/editar/<int:venta_id>/',editar_venta,name='editar_venta'),
    path('historial/exportar/excel/',exportar_historial_ventas_excel,name='exportar_historial_ventas_excel'),
    path('historial/exportar/pdf/',exportar_historial_ventas_pdf,name='exportar_historial_ventas_pdf'),
    path('informes/historial/',historial_ventas,name='historial_ventas'),
    path('informes/detalle/',detalle_ventas,name='detalle_ventas'),
    path('informes/por-categoria/',ventas_por_categoria,name='ventas_por_categoria'),
    path('informes/por-categoria/exportar/excel/',exportar_ventas_categoria_excel,name='exportar_ventas_categoria_excel'),
    path('informes/por-categoria/exportar/pdf/',exportar_ventas_categoria_pdf,name='exportar_ventas_categoria_pdf'),    
    path('informes/detalle/exportar/excel/',exportar_detalle_ventas_excel,name='exportar_detalle_ventas_excel'),
    path('informes/detalle/exportar/pdf/',exportar_detalle_ventas_pdf,name='exportar_detalle_ventas_pdf'),
]