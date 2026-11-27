"""
Django settings for vogue project.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS — loaded from environment variables
# ==============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# 'prod' env var is the production flag (set to 'true' on the server)
IS_PROD = os.environ.get('prod', 'false').lower() == 'true'
DEBUG = not IS_PROD

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Git revision — useful for sentry, health-check endpoints, etc.
GIT_REV = os.environ.get('GIT_REV', 'unknown')


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vogue.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vogue.wsgi.application'


# ==============================================================================
# DATABASE
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
# Reads DATABASE_URL env var (e.g. postgres://user:pass@host:5432/dbname)
# Falls back to local SQLite for development.
# ==============================================================================

_DATABASE_URL = os.environ.get('DATABASE_URL', '')
if _DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            _DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==============================================================================
# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators
# ==============================================================================

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


# ==============================================================================
# INTERNATIONALIZATION
# https://docs.djangoproject.com/en/6.1/topics/i18n/
# ==============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ==============================================================================
# STATIC & MEDIA FILES
# Static files are served by WhiteNoise (from staticfiles/).
# Media/uploads are stored in MinIO (S3-compatible) in production.
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

_MINIO_ENDPOINT  = os.environ.get('minio_endpoint', '')   # e.g. minio.alcheringa.co.in
_MINIO_ACCESS    = os.environ.get('minio_access', '')
_MINIO_SECRET    = os.environ.get('minio_secret', '')

if IS_PROD and _MINIO_ENDPOINT:
    # Serve media files from MinIO (S3-compatible object storage)
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    AWS_ACCESS_KEY_ID       = _MINIO_ACCESS
    AWS_SECRET_ACCESS_KEY   = _MINIO_SECRET
    AWS_STORAGE_BUCKET_NAME = os.environ.get('minio_bucket', 'vogue-media')
    AWS_S3_ENDPOINT_URL     = f'https://{_MINIO_ENDPOINT}'
    AWS_S3_FILE_OVERWRITE   = False
    AWS_DEFAULT_ACL         = 'public-read'
    AWS_QUERYSTRING_AUTH    = False   # Public URLs without signed params
    MEDIA_URL = f'https://{_MINIO_ENDPOINT}/{AWS_STORAGE_BUCKET_NAME}/'
else:
    # Local dev: serve media from filesystem
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# SECURITY SETTINGS (enforced when DEBUG=False)
# ==============================================================================

if IS_PROD:
    # Dokku/Traefik handles SSL termination — Django should NOT redirect itself.
    # Having SECURE_SSL_REDIRECT=True behind a proxy causes CSRF cookies to drop
    # during the HTTP→HTTPS redirect loop.
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Trust the X-Forwarded-Proto header set by Traefik
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Explicitly trust all production domains for CSRF.
    # Django requires these to match the Origin header on cross-origin POST requests.
    CSRF_TRUSTED_ORIGINS = [
        'https://prelims.alcheringa.co.in',
        'https://ceportal.alcheringa.co.in',
        'https://highwaytoalcher.alcheringa.co.in',
    ]

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


# ==============================================================================
# EMAIL
# https://docs.djangoproject.com/en/6.1/topics/email/
# ==============================================================================

if IS_PROD:
    EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST         = 'smtp.gmail.com'
    EMAIL_PORT         = 587
    EMAIL_USE_TLS      = True
    EMAIL_HOST_USER    = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
    },
}


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
