# Generated manually for POS Perú.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0007_alter_venta_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='tipo_comprobante',
            field=models.CharField(
                choices=[
                    ('BOLETA', 'Boleta'),
                    ('FACTURA', 'Factura'),
                    ('TICKET', 'Ticket interno'),
                ],
                default='BOLETA',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='serie_comprobante',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='venta',
            name='numero_comprobante',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
