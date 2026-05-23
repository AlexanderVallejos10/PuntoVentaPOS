from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from inventario.models import Sede


class Caja(models.Model):
    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT
    )

    nombre = models.CharField(
        max_length=100
    )

    activa = models.BooleanField(
        default=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.nombre} - {self.sede.nombre}'


class AperturaCaja(models.Model):
    TURNO_CHOICES = (
        ('MANANA', 'Mañana'),
        ('TARDE', 'Tarde'),
        ('NOCHE', 'Noche'),
    )

    ESTADO_CHOICES = (
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    )

    caja = models.ForeignKey(
        Caja,
        on_delete=models.PROTECT
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    turno = models.CharField(
        max_length=20,
        choices=TURNO_CHOICES
    )

    monto_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    monto_contado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    monto_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    diferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ABIERTA'
    )

    fecha_apertura = models.DateTimeField(
        auto_now_add=True
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True
    )

    def calcular_monto_esperado(self):
        ingresos = self.movimientos.filter(
            tipo='INGRESO'
        ).aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')

        salidas = self.movimientos.filter(
            tipo='SALIDA'
        ).aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')

        return self.monto_inicial + ingresos - salidas

    def cerrar(self, monto_contado):
        self.monto_contado = Decimal(str(monto_contado))
        self.monto_esperado = self.calcular_monto_esperado()
        self.diferencia = self.monto_contado - self.monto_esperado
        self.estado = 'CERRADA'
        self.fecha_cierre = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.caja.nombre} - {self.usuario.username} - {self.turno}'


class MovimientoCaja(models.Model):
    TIPO_CHOICES = (
        ('INGRESO', 'Ingreso'),
        ('SALIDA', 'Salida'),
    )

    apertura = models.ForeignKey(
        AperturaCaja,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )

    venta = models.ForeignKey(
        'ventas.Venta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )

    concepto = models.CharField(
        max_length=255
    )

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.tipo} - S/ {self.monto}'