"""
Django settings for Sigma-ALS Multi-Sector AI Learning Platform
Optimized for African educational contexts with offline-first capability
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.multi_sector',
    'apps.ai_engine',
    'apps.teacher_oversight',
    'apps.offline_sync',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sigma_als.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'sigma_als.wsgi.application'
ASGI_APPLICATION = 'sigma_als.asgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sigmaals'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    } if not DEBUG else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache configuration (Redis for production, local memory for development)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    } if not DEBUG else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# CORS configuration for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in development

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sigma-ALS API',
    'DESCRIPTION': 'Multi-Sector AI Learning Assistant for African Education',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# AI Integration Settings
AI_SETTINGS = {
    'OPENAI_API_KEY': config('OPENAI_API_KEY', default=''),
    'MODEL_VERSION': config('AI_MODEL_VERSION', default='gpt-3.5-turbo'),
    'MAX_TOKENS': config('AI_MAX_TOKENS', default=1000, cast=int),
    'TEMPERATURE': config('AI_TEMPERATURE', default=0.7, cast=float),
    'TIMEOUT': 30,  # seconds
}

# Multi-Sector Configuration
SECTOR_CONFIGS = {
    'mathematics': {
        'enabled': True,
        'curriculum_standard': 'uganda_uneb',
        'language_support': ['en', 'lg'],  # English, Luganda
        'cultural_context': 'east_africa',
        'offline_priority': 'medium',
    },
    'agriculture': {
        'enabled': True,
        'regional_adaptation': 'east_africa',
        'currency_support': ['UGX', 'KES', 'TZS'],  # Uganda, Kenya, Tanzania
        'cultural_context': 'rural_farming',
        'offline_priority': 'high',  # Critical for rural deployment
    },
    'tvet': {
        'enabled': True,
        'standards_framework': 'qcto_south_africa',
        'language_support': ['en', 'af'],  # English, Afrikaans  
        'industry_integration': True,
        'offline_priority': 'low',  # Usually better connectivity
    }
}

# Teacher Oversight System
TEACHER_OVERSIGHT = {
    'REVIEW_REQUIRED': config('TEACHER_REVIEW_REQUIRED', default=True, cast=bool),
    'AUTO_APPROVE_THRESHOLD': config('AUTO_APPROVE_CONFIDENCE_THRESHOLD', default=0.95, cast=float),
    'CULTURAL_SENSITIVITY_THRESHOLD': config('CULTURAL_SENSITIVITY_THRESHOLD', default=0.85, cast=float),
    'REVIEW_TIMEOUT_HOURS': config('REVIEW_TIMEOUT_HOURS', default=24, cast=int),
    'ESCALATION_ENABLED': True,
}

# Offline Sync Configuration  
OFFLINE_SYNC = {
    'CACHE_SIZE_MB': config('OFFLINE_CACHE_SIZE_MB', default=50, cast=int),
    'RETRY_ATTEMPTS': config('SYNC_RETRY_ATTEMPTS', default=3, cast=int),
    'BATCH_SIZE': config('SYNC_BATCH_SIZE', default=100, cast=int),
    'PRIORITY_SECTORS': ['agriculture', 'mathematics', 'tvet'],
}

# Regional and Cultural Settings
REGIONAL_SETTINGS = {
    'DEFAULT_REGION': config('DEFAULT_REGION', default='east_africa'),
    'SUPPORTED_LANGUAGES': config('SUPPORTED_LANGUAGES', default='en,sw,lg,af').split(','),
    'DEFAULT_CURRENCY': config('DEFAULT_CURRENCY', default='USD'),
    'TIMEZONE_MAPPING': {
        'east_africa': 'Africa/Nairobi',
        'west_africa': 'Africa/Lagos', 
        'southern_africa': 'Africa/Johannesburg',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'sigma_als.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.ai_engine': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Ensure logs directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Security settings (production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sigma-als.org')

# Sentry configuration for error monitoring
if config('SENTRY_DSN', default=''):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
