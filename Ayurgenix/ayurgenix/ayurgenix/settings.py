"""
Django settings for ayurgenix project.
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q1^wd4u=uddg4#y(wb8nvihr^$0g0pz8d4a7!x4m_kd^cz07n^'

# 🔹 Allowed Hosts (Ensure Django Accepts Requests)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# 🔹 CSRF Trusted Origins (Prevents CSRF Errors)
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    # "https://yourdomain.com",  # Add your live domain here when deploying
]

# 🔹 CSRF Security Settings
CSRF_USE_SESSIONS = True  # Store CSRF token in session instead of cookies
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing CSRF cookies

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

EXTERNAL_APPS = [
    'home',
]

INSTALLED_APPS += EXTERNAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'ayurgenix.urls'

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'home', 'templates'),
        ],
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

WSGI_APPLICATION = 'ayurgenix.wsgi.application'

# Database Configuration (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ayurgenix',
        'USER': 'postgres',
        'PASSWORD': 'NIKIta12@#',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
