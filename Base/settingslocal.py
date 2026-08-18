"""
Django settings for Portfolio project - DESARROLLO LOCAL

Para más información:
https://docs.djangoproject.com/en/4.2/topics/settings/
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r%+gt7d^8wj8^@j2cb2x!tvnwm8(i@mxoa3!#85+n=rpo@hk*0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'Base.Core',
    'django_cleanup.apps.CleanupConfig',  # SIEMPRE al final
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'resources', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Base.wsgi.application'

# Database - PostgreSQL LOCAL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME_LOCAL'),
        'USER': config('DB_USER_LOCAL'),
        'PASSWORD': config('DB_PASSWORD_LOCAL'),
        'HOST': config('DB_HOST_LOCAL', default='localhost'),
        'PORT': config('DB_PORT_LOCAL', default='5432'),
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) - LOCAL
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(RESOURCES_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# AWS S3 Configuration (LOCAL)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Media files - S3 (LOCAL)
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media-dev/'
STORAGES = {
    "default": {"BACKEND": "Base.storagemedia.MediaStorageDev",},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",},
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'