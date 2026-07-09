from django.db import models

from clientes.models import Cliente
from inventario.models import Sede


class Venta(models.Model):
    ESTADO_CHOICES = (
        ('PAGADA', 'Pagada'),
        ('ESPERA', 'Espera'),
        ('ANULADA', 'Anulada'),
        ('DEVUELTA', 'Devuelta'),
    )

    METODOS_PAGO = (
        ('EFECTIVO', 'EFECTIVO'),
        ('YAPE', 'YAPE'),
        ('PLIN', 'PLIN'),
        ('TARJETA', 'TARJETA'),
    )

    TIPO_COMPROBANTE = (
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('TICKET', 'Ticket interno'),
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    tipo_comprobante = models.CharField(
        max_length=20,
        choices=TIPO_COMPROBANTE,
        default='BOLETA',
    )

    serie_comprobante = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    numero_comprobante = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='EFECTIVO',
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PAGADA',
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cortesia = models.BooleanField(default=False)

    envio_domicilio = models.BooleanField(default=False)
    origen_envio = models.CharField(max_length=255, blank=True, null=True)
    destino_envio = models.CharField(max_length=255, blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True)

    @property
    def comprobante_codigo(self):
        serie = self.serie_comprobante or self.serie_por_defecto
        numero = self.numero_comprobante or f'{self.id or 0:08d}'
        return f'{serie}-{numero}'

    @property
    def comprobante_nombre(self):
        return dict(self.TIPO_COMPROBANTE).get(self.tipo_comprobante, 'Comprobante')

    @property
    def serie_por_defecto(self):
        if self.tipo_comprobante == 'FACTURA':
            return 'F001'

        if self.tipo_comprobante == 'TICKET':
            return 'T001'

        return 'B001'

    def asignar_numero_comprobante(self):
        if not self.serie_comprobante:
            self.serie_comprobante = self.serie_por_defecto

        if not self.numero_comprobante and self.id:
            self.numero_comprobante = f'{self.id:08d}'

    def __str__(self):
        return f'{self.comprobante_nombre} {self.comprobante_codigo}'
