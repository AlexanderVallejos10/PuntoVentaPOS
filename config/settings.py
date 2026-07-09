from pathlib import Path
from decouple import config
from importlib.util import find_spec

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-local-development-key-change-in-production'
)

DEBUG = config('DEBUG', cast=bool, default=True)

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        'ALLOWED_HOSTS',
        default='localhost,127.0.0.1,[::1]'
    ).split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'usuarios',
    'productos',
    'ventas',
    'clientes',
    'inventario',
    'compras',
    'gastos',
    'django.contrib.humanize',
]

DEFAULT_RECAPTCHA_PUBLIC_KEY = '6LfvAPcsAAAAALsIjdM_zGllMnyl7Ezj8OI5dWan'
DEFAULT_RECAPTCHA_PRIVATE_KEY = '6LfvAPcsAAAAABxM-GUog9-7VzkCYXn4dx5uR4Mg'


def valor_config(nombre, default=''):
    valor = config(nombre, default=default)

    if isinstance(valor, str):
        valor = valor.strip()

    return valor or default


RECAPTCHA_PUBLIC_KEY = valor_config(
    'RECAPTCHA_PUBLIC_KEY',
    DEFAULT_RECAPTCHA_PUBLIC_KEY
)
RECAPTCHA_PRIVATE_KEY = valor_config(
    'RECAPTCHA_PRIVATE_KEY',
    DEFAULT_RECAPTCHA_PRIVATE_KEY
)

RECAPTCHA_ACTIVO = bool(
    RECAPTCHA_PUBLIC_KEY
    and RECAPTCHA_PRIVATE_KEY
    and find_spec('django_recaptcha')
)

if RECAPTCHA_ACTIVO:
    INSTALLED_APPS.append('django_recaptcha')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'inventario.context_processors.empresa_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3').strip()
DB_NAME = config('DB_NAME', default='').strip()

if not DB_ENGINE:
    DB_ENGINE = 'django.db.backends.sqlite3'

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME or str(BASE_DIR / 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': config('DB_USER', default=''),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default=''),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/ventas/'
LOGOUT_REDIRECT_URL = '/login/'
