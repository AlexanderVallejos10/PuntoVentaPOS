from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

IGV = Decimal('0.18')
MONTO_DOCUMENTO_OBLIGATORIO = Decimal('700.00')

TIPO_BOLETA = 'BOLETA'
TIPO_FACTURA = 'FACTURA'
TIPO_TICKET = 'TICKET'
TIPOS_COMPROBANTE = {TIPO_BOLETA, TIPO_FACTURA, TIPO_TICKET}


def dinero(valor):
    try:
        monto = Decimal(str(valor or '0'))
    except (InvalidOperation, ValueError):
        monto = Decimal('0')

    return monto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def limpiar_documento(numero):
    return ''.join(str(numero or '').strip().split())


def documento_valido(tipo_documento, numero_documento):
    tipo = (tipo_documento or 'SD').upper().strip()
    numero = limpiar_documento(numero_documento)

    if tipo == 'SD':
        return True

    if tipo == 'DNI':
        return numero.isdigit() and len(numero) == 8

    if tipo == 'RUC':
        return numero.isdigit() and len(numero) == 11

    if tipo == 'CE':
        return len(numero) >= 6

    return False


def cliente_identificado(cliente):
    if not cliente:
        return False

    tipo = (cliente.tipo_documento or 'SD').upper().strip()
    numero = cliente.numero_documento or ''

    return tipo != 'SD' and documento_valido(tipo, numero)


def requiere_documento(total):
    return dinero(total) > MONTO_DOCUMENTO_OBLIGATORIO


def normalizar_tipo_comprobante(tipo_comprobante):
    tipo = (tipo_comprobante or TIPO_BOLETA).upper().strip()
    return tipo if tipo in TIPOS_COMPROBANTE else TIPO_BOLETA


def serie_por_tipo(tipo_comprobante):
    tipo = normalizar_tipo_comprobante(tipo_comprobante)

    if tipo == TIPO_FACTURA:
        return 'F001'

    if tipo == TIPO_TICKET:
        return 'T001'

    return 'B001'


def validar_cliente_venta(total, cliente, tipo_comprobante=TIPO_BOLETA):
    tipo = normalizar_tipo_comprobante(tipo_comprobante)

    if tipo == TIPO_FACTURA:
        if not cliente or cliente.tipo_documento != 'RUC' or not documento_valido('RUC', cliente.numero_documento):
            return False, 'Para emitir factura selecciona un cliente con RUC válido.'

    if requiere_documento(total) and not cliente_identificado(cliente):
        return False, 'Para ventas mayores a S/ 700 registra el documento del cliente.'

    return True, ''


def calcular_totales(subtotal, descuento_porcentaje=0, costo_envio=0, cortesia=False, envio_domicilio=False):
    subtotal = dinero(subtotal)
    descuento_porcentaje = dinero(descuento_porcentaje)

    if descuento_porcentaje < 0:
        descuento_porcentaje = Decimal('0.00')

    if descuento_porcentaje > 100:
        descuento_porcentaje = Decimal('100.00')

    costo_envio = dinero(costo_envio) if envio_domicilio else Decimal('0.00')

    if cortesia:
        return {
            'cortesia': True,
            'envio_domicilio': False,
            'descuento': subtotal,
            'impuesto': Decimal('0.00'),
            'costo_envio': Decimal('0.00'),
            'total': Decimal('0.00'),
        }

    descuento = dinero(subtotal * descuento_porcentaje / Decimal('100'))
    base = subtotal - descuento
    impuesto = dinero(base * IGV)
    total = dinero(base + impuesto + costo_envio)

    return {
        'cortesia': False,
        'envio_domicilio': envio_domicilio,
        'descuento': descuento,
        'impuesto': impuesto,
        'costo_envio': costo_envio,
        'total': total,
    }
