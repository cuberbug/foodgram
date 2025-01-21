# flake8: noqa
"""
Настройки для бэкенда "Фудграм".

Расширены использованием дополнительных инструментов для взаимодействия
с переменными окружения и логгером.
"""
from pathlib import Path

from environs import Env

# Управление переменными окружения

env = Env()
env.read_env()

# Basic variables

AUTH_USER_MODEL = 'users.User'
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
BASE_DIR = Path(__file__).resolve().parent.parent
PAGINATION_SIZE = env.int('PAGINATION_SIZE', 6)

# Security settings

SECRET_KEY = env.str('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

# Develop

if env.bool('DEV'):
    DJANGO_SUPERUSER_USERNAME = 'admin'
    DJANGO_SUPERUSER_EMAIL = 'admin@example.com'
    DJANGO_SUPERUSER_PASSWORD = 'adminpass'


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': env.str('HANDLER_FILE_LEVEL', 'DEBUG'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': f'{BASE_DIR}/logs/logfile.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 21,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env.str('LOGGER_DJANGO_LEVEL', 'WARNING'),
            'propagate': True,
        },
    },
}


# Application definition

INSTALLED_APPS = [
    # Base libs
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Extra libs
    'django_filters',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',

    # Applications
    'api',
    'food',
    'users',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database

SQLITE: str = 'sqlite'
POSTGRESQL: str = 'postgresql'
DATABASE_NAME: str = SQLITE if DEBUG and env.bool('SQLITE') else POSTGRESQL

DATABASES = {
    SQLITE: {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    POSTGRESQL: {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB', 'django'),
        'USER': env.str('POSTGRES_USER', 'django'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', ''),
        'HOST': env.str('POSTGRES_HOST', ''),
        'PORT': env.int('POSTGRES_PORT', 5432),
    }
}
DATABASES['default'] = DATABASES[DATABASE_NAME]


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

LANGUAGE_CODE = env.str('LANGUAGE_CODE', 'en-us')

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'django_static/'
STATIC_ROOT = BASE_DIR / 'backend_static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', 
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': PAGINATION_SIZE,
}


# Djoser

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'USER_ID_FIELD': 'pk',
    'SERIALIZERS': {
        'user_create': 'api.serializers.CustomUserCreateSerializer',
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    }
}
