from decimal import Decimal

from django.shortcuts import get_object_or_404

from inventario.models import StockBodega
from productos.models import Producto
from ventas.models import DetalleVenta
from ventas.services.reglas_peru import dinero


def cantidad_item(item):
    try:
        return int(item.get('cantidad', 0))
    except (TypeError, ValueError):
        return 0


def stock_sede(producto, sede, bloquear=False):
    consulta = StockBodega.objects.filter(
        producto=producto,
        sede=sede,
        activo=True,
    )

    if bloquear:
        consulta = consulta.select_for_update()

    return consulta.first()


def validar_stock_carrito(carrito, sede):
    if not sede:
        return False, 'No hay sede seleccionada para vender.'

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = cantidad_item(item)

        if cantidad <= 0:
            return False, f'Cantidad inválida para {producto.nombre}.'

        stock = stock_sede(producto, sede)

        if not stock:
            return False, f'{producto.nombre} no tiene stock en la sede {sede.nombre}.'

        if cantidad > stock.stock:
            return False, f'Stock insuficiente para {producto.nombre}. Disponible en {sede.nombre}: {stock.stock}.'

    return True, ''


def calcular_subtotal_carrito(carrito):
    subtotal = Decimal('0.00')

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        subtotal += producto.precio_venta * cantidad_item(item)

    return dinero(subtotal)


def registrar_detalles_y_stock(venta, carrito, sede):
    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = cantidad_item(item)
        stock = stock_sede(producto, sede, bloquear=True)

        if not stock:
            raise ValueError(f'{producto.nombre} no tiene stock en esta sede.')

        if cantidad <= 0:
            raise ValueError(f'Cantidad inválida para {producto.nombre}.')

        if cantidad > stock.stock:
            raise ValueError(f'Stock insuficiente para {producto.nombre}. Disponible: {stock.stock}.')

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=dinero(producto.precio_venta * cantidad),
        )

        stock.stock -= cantidad
        stock.save(update_fields=['stock'])
