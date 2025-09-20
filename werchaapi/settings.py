"""
Django settings for werchaapi project.
Clean, env-driven, production-ready.
"""

import os
from pathlib import Path
import environ

# ────────────────────────────────────────────────────────────────────────────────
# Paths & Env
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# .env محلی برای توسعه (روی سرور نیازی نیست)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='dev-insecure-override-me')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ────────────────────────────────────────────────────────────────────────────────
# Apps
# ────────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'accounts',
    'catalog',
    'orders',
    'blog',

    # Third-party
    'rest_framework',
    'corsheaders',
]

# ────────────────────────────────────────────────────────────────────────────────
# Middleware
# ────────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # باید اول از CommonMiddleware باشد
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ────────────────────────────────────────────────────────────────────────────────
# URLs / WSGI / TEMPLATES
# ────────────────────────────────────────────────────────────────────────────────
ROOT_URLCONF = 'werchaapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'werchaapi.wsgi.application'

# ────────────────────────────────────────────────────────────────────────────────
# Database (env-driven; default = sqlite for dev)
# ────────────────────────────────────────────────────────────────────────────────
# مثال env در سرور:
# DATABASE_URL=postgres://werch_user:STRONG_PASS@postgres:5432/werch_db
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)

# ────────────────────────────────────────────────────────────────────────────────
# Auth
# ────────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.auth_backends.EmailOrUsernameBackend',
]

# ────────────────────────────────────────────────────────────────────────────────
# DRF
# ────────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',   # ← جدید
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',           # ← افزایش برای مهمان‌ها
        'user': '20000/day',
        'login': '5/min',
        'public_read': '300/min',     # ← اسکوپ جدید برای GETهای عمومی (بلاگ/کاتالوگ)
    },
}

# ────────────────────────────────────────────────────────────────────────────────
# i18n / tz
# ────────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ────────────────────────────────────────────────────────────────────────────────
# Static / Media
# ────────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = BASE_DIR / 'staticfiles'   # برای collectstatic در پرود
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ────────────────────────────────────────────────────────────────────────────────
# CORS / CSRF (از ENV بخوان)
# ────────────────────────────────────────────────────────────────────────────────
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:3000'])

# ────────────────────────────────────────────────────────────────────────────────
# Security (همه از ENV قابل کنترل)
# ────────────────────────────────────────────────────────────────────────────────
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # فرانت نیاز به خواندن CSRF دارد
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# وقتی SSL ندارید → SECURE_SSL_REDIRECT=False در ENV سرور
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=not DEBUG)

SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE   = env.bool('CSRF_COOKIE_SECURE',   default=not DEBUG)

SECURE_HSTS_SECONDS            = env.int('SECURE_HSTS_SECONDS', default=(0 if DEBUG else 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG)
SECURE_HSTS_PRELOAD            = env.bool('SECURE_HSTS_PRELOAD', default=not DEBUG)

# پشت Nginx/Proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
