from django import forms
from productos.models import Categoria
from inventario.models import StockBodega


class StockBodegaForm(forms.ModelForm):

    nombre = forms.CharField(
        label='Nombre del producto',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. COCA COLA botella 1L'})
    )

    categoria = forms.ModelChoiceField(
        label='Categoría',
        queryset=Categoria.objects.filter(activo=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    descripcion = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve del producto'})
    )

    precio_compra = forms.DecimalField(
        label='Valor de compra',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'})
    )

    precio_venta = forms.DecimalField(
        label='Valor de venta',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'})
    )

    imagen_url = forms.URLField(
        label='URL de imagen',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://.../imagen.jpg'})
    )

    class Meta:
        model = StockBodega

        fields = [
            'sede',
            'stock',
            'stock_minimo',
            'activo',
        ]

        widgets = {
            'sede': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }