"""
Django settings for FAIRmodels_backend project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv('SECRET_KEY', 'django-insecure-1234'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    'api.fairmodels.org'
]

CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',

    'django_extensions',
    
    'allauth',
    'allauth.account',
    
    'dj_rest_auth.registration',
    
    'corsheaders',

    'api'
]

# https://dj-rest-auth.readthedocs.io/en/latest/installation.html#registration-optional
SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'FAIRmodels_backend.urls'

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

WSGI_APPLICATION = 'FAIRmodels_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

REST_AUTH = {
    'REGISTER_SERIALIZER': 'dj_rest_auth.registration.serializers.RegisterSerializer',
    
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False # https://stackoverflow.com/a/75598507
}

# cors

CORS_ALLOWED_ORIGINS = [
    'http://localhost:9000',
    'https://*.fairmodels.org'
]
CSRF_TRUSTED_ORIGINS = [
    'https://*.fairmodels.org'
]
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'api.fairmodels.org',
]
CORS_ORIGIN_WHITELIST = [
    'https://api.fairmodels.org',
    'https://models.fairmodels.org',
    'http://localhost:8000',
    'http://localhost:9000'
]

# allauth configuration

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none' # https://stackoverflow.com/a/56569472

# APPEND_SLASH=False

# Disable username and use email as primary (from https://stackoverflow.com/a/66497346/17864167)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
# Update: according to: https://github.com/pennersr/django-allauth/issues/1014#issuecomment-121245406
# following field should be usernmae instead of None
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1), # TODO: shorten for production
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True
}

# Following is added to enable registration with email instead of username
AUTHENTICATION_BACKENDS = (
 # Needed to login by username in Django admin, regardless of `allauth`
 "django.contrib.auth.backends.ModelBackend",
 # `allauth` specific authentication methods, such as login by e-mail
 "allauth.account.auth_backends.AuthenticationBackend",
)

# Metadatacendar Config Options

METADATACENTER_INSTANCES_FOLDER_ID = os.getenv('METADATACENTER_INSTANCES_FOLDER_ID', '6ce6f9ff-a9ff-49a0-987a-88d3c9b639ff')
METADATACENTER_TEMPLATE_ID = ''
METADATACENTER_FIELD_INPUT_ID = os.getenv('METADATACENTER_FIELD_INPUT_PROPERTY_URI', 'https://schema.metadatacenter.org/properties/6b6846ba-4e4f-44d4-8349-12147de2cda5')
METADATACENTER_FIELD_OUTPUT_ID = os.getenv('METADATACENTER_FIELD_OUTPUT_PROPERTY_URI', 'https://schema.metadatacenter.org/properties/9cb9445b-3f63-48d3-8989-e2444e2b9a45')