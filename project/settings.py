from pathlib import Path
import os
import json
from loguru import logger
import sys
from datetime import datetime
from dotenv import load_dotenv
from django_components import ComponentsSettings

# Cargar variables de entorno desde .env
load_dotenv(override=True)

# Configuración de Loguru
LOGURU_CONFIG = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": "INFO",
        }
    ]
}

# En producción, agregar el handler de S3
if not os.environ.get('IS_LOCAL') == 'True':
    LOGURU_CONFIG["handlers"].append({
        "sink": f"s3://{os.environ['AWS_STORAGE_BUCKET_NAME']}/logs/app_{datetime.now().strftime('%Y-%m-%d')}.log",
        "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        "level": "DEBUG",
        "rotation": "1 day",
        "retention": "30 days",
    })

# Configurar Loguru
logger.configure(**LOGURU_CONFIG)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ['DEBUG'] == 'True'
IS_LOCAL = os.environ.get('IS_LOCAL') == 'True'

ALLOWED_HOSTS = [
    '*.amazonaws.com',
    '*.apprunner.aws',
    '*.awsapprunner.com',
    f'*.{os.environ["AWS_S3_REGION_NAME"]}.awsapprunner.com',
    'csjqtfjiu7.us-east-1.awsapprunner.com',  # Dominio específico como respaldo
    'localhost',
    '127.0.0.1'
]

CSRF_TRUSTED_ORIGINS = [  # Dominios permitidos para peticiones POST con token CSRF
    'https://*.amazonaws.com',
    'https://*.apprunner.aws',
    'https://*.awsapprunner.com',
    'http://localhost:8080',
    'http://127.0.0.1:8080'
]

CSRF_COOKIE_SECURE = True  # Fuerza HTTPS para cookie CSRF
SESSION_COOKIE_SECURE = True  # Fuerza HTTPS para cookie de sesión
CSRF_COOKIE_SAMESITE = 'Strict'  # Previene envío de cookie CSRF en peticiones cross-site
SESSION_COOKIE_SAMESITE = 'Strict'  # Previene envío de cookie de sesión en peticiones cross-site
CSRF_USE_SESSIONS = True  # Almacena token CSRF en sesión en lugar de cookie
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Detecta HTTPS detrás del proxy de App Runner

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_components',
    'django_vite',
    'django_htmx',
    'storages',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'django_components.templatetags.component_tags',
            ],
            'loaders': [(
                'django.template.loaders.cached.Loader', [
                    # Loader por defecto de Django
                    'django.template.loaders.filesystem.Loader',
                    # Incluir esto es equivalente a APP_DIRS=True
                    'django.template.loaders.app_directories.Loader',
                    # Loader de componentes
                    'django_components.template_loader.Loader',
                ]
            )],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USERNAME'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de S3
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_OBJECT_PARAMETERS = json.loads(os.environ.get('AWS_S3_OBJECT_PARAMETERS', '{"CacheControl": "max-age=86400"}'))
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_VERIFY = True

# Archivos estáticos y multimedia
VITE_ASSETS_PATH = BASE_DIR / "static" / "dist"

STATICFILES_FINDERS = [
    # Buscadores por defecto
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # Buscador de componentes Django
    "django_components.finders.ComponentsFileSystemFinder",
]

STATICFILES_DIRS = [
    VITE_ASSETS_PATH,
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

DJANGO_VITE = {
    "default": {
        "dev_mode": IS_LOCAL,  # Solo modo desarrollo cuando está ejecutándose localmente
        "manifest_path": VITE_ASSETS_PATH / "manifest.json",
    }
}

if IS_LOCAL:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'mediafiles'
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    if not all([AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, AWS_S3_CUSTOM_DOMAIN]):
        logger.warning("Configuración de S3 incompleta.")
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "custom_domain": AWS_S3_CUSTOM_DOMAIN,
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "location": "static",
                "custom_domain": AWS_S3_CUSTOM_DOMAIN,
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            },
        },
    }
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Ejecutor de pruebas
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configuración de django-components según documentación oficial
COMPONENTS = ComponentsSettings(
    dirs=[
        BASE_DIR / "components",
    ],
)
