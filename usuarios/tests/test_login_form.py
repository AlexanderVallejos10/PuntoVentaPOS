from django.test import SimpleTestCase
from django.test import override_settings

from usuarios.forms import LoginForm


class LoginFormTests(SimpleTestCase):

    @override_settings(RECAPTCHA_ENABLED=False)
    def test_login_form_skips_captcha_when_disabled(self):
        form = LoginForm()

        self.assertNotIn('captcha', form.fields)

    @override_settings(RECAPTCHA_ENABLED=True)
    def test_login_form_includes_captcha_when_enabled(self):
        form = LoginForm()

        self.assertIn('captcha', form.fields)
