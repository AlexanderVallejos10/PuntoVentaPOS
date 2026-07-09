from django import forms
from django.conf import settings

try:
    from django_recaptcha.fields import ReCaptchaField
    from django_recaptcha.widgets import ReCaptchaV2Checkbox
except ImportError:
    ReCaptchaField = None
    ReCaptchaV2Checkbox = None


class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Usuario',
                'autocomplete': 'username',
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Contraseña',
                'autocomplete': 'current-password',
            }
        )
    )

    if settings.RECAPTCHA_ACTIVO and ReCaptchaField:
        captcha = ReCaptchaField(
            widget=ReCaptchaV2Checkbox
        )
    else:
        captcha = forms.CharField(
            required=False,
            widget=forms.HiddenInput
        )
