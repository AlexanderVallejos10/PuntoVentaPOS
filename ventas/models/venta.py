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

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='EFECTIVO'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PAGADA'
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

    def __str__(self):
        return f'Venta #{self.id}'
    
    