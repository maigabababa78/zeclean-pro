"""
Django settings for cleanpro_project.
Application de Gestion d'une Société de Nettoyage (CleanPro ERP).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'cleanpro-dev-secret-key-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,*').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core.apps.CoreConfig',
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

ROOT_URLCONF = 'cleanpro_project.urls'

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
                'core.context_processors.company_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'cleanpro_project.wsgi.application'

# Configuration Base de données : PostgreSQL ou bascule SQLite locale
USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', 'False').lower() in ('true', '1', 'yes')

if USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'cleanpro_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'core.User'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Paramètres métier (Devise CFA & Fiscalité)
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'FCFA')
DEFAULT_TVA_RATE = float(os.getenv('DEFAULT_TVA_RATE', '18.0'))
COMPANY_NAME = os.getenv('COMPANY_NAME', 'ZeClean Pro SARL')
COMPANY_PHONE = os.getenv('COMPANY_PHONE', '+221 33 800 00 00')
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL', 'contact@zeclean-pro.com')
COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS', 'Avenue Jean-Paul II, Zone Industrielle')
COMPANY_RC = os.getenv('COMPANY_RC', 'RC-DKR-2026-B-14520')
COMPANY_NINEA = os.getenv('COMPANY_NINEA', 'NINEA-008451236')
