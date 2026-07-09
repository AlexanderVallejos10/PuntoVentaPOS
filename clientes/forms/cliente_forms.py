from django import forms

from clientes.models import Cliente
from ventas.services.reglas_peru import documento_valido, limpiar_documento


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'tipo_documento',
            'numero_documento',
            'nombre',
            'telefono',
            'email',
            'direccion',
            'activo',
        ]
        labels = {
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'nombre': 'Nombre / razón social',
            'telefono': 'Teléfono',
            'email': 'Correo electrónico',
            'direccion': 'Dirección',
            'activo': 'Activo',
        }
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_documento',
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DNI, RUC o CE',
                'id': 'id_numero_documento',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente o razón social',
                'id': 'id_nombre',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean_numero_documento(self):
        tipo = (self.cleaned_data.get('tipo_documento') or 'SD').upper()
        numero = limpiar_documento(self.cleaned_data.get('numero_documento'))

        if tipo == 'SD':
            return ''

        if not documento_valido(tipo, numero):
            raise forms.ValidationError('Revise el número de documento.')

        return numero
