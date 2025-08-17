"""
Configuración de Django para el proyecto.

Este archivo define los ajustes principales de la aplicación web:
- Rutas de plantillas y apps instaladas (INSTALLED_APPS, MIDDLEWARE, TEMPLATES, WSGI).
- Base de datos por defecto (SQLite para desarrollo).
- Integración opcional con MongoDB Atlas vía mongoengine si se define MONGO_URI.
- Parámetros de internacionalización, archivos estáticos y claves de seguridad.

Variables de entorno relevantes (recomendado configurarlas en .env o en el entorno del despliegue):
- ALLOWED_HOSTS: lista separada por comas con los hosts permitidos (p.ej. "miapp.com,www.miapp.com").
- CSRF_TRUSTED_ORIGINS: lista separada por comas de orígenes confiables para CSRF (p.ej. "https://miapp.com,https://*.miapp.com").
- MONGO_URI: cadena de conexión a MongoDB (si no se define, se omite la conexión y se registra un warning).
- OAUTH_CLIENT_ID, OAUTH_AUTH_ENDPOINT, OAUTH_REDIRECT_URI, OAUTH_TOKEN_ENDPOINT, OAUTH_SCOPE: ajustes usados por las vistas OAuth2 (api/views/login.py).

Notas de seguridad:
- SECRET_KEY no debe exponerse en repositorios públicos; define un valor seguro en producción vía variables de entorno.
- DEBUG debe ser False en producción. Este archivo deja el valor tal cual para desarrollo, pero ajústalo al desplegar.

Base de datos:
- SQLite (django.db.backends.sqlite3) como base por defecto para el stack de Django.
- MongoDB (opcional) para modelos con mongoengine. La conexión intenta establecerse al inicio con un timeout bajo
  (serverSelectionTimeoutMS=5000) y registra un warning si falla para no bloquear el arranque.

Más información:
- Documentación de settings: https://docs.djangoproject.com/en/4.2/ref/settings/
- Internacionalización: https://docs.djangoproject.com/en/4.2/topics/i18n/
"""

from pathlib import Path
from dotenv import load_dotenv
import mongoengine
import os
import logging

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w$6r-+@n&=lnn9$g&qc+8y^r%*x)8r=t9uaj4!7zv@xgo_m4^3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "true"


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Confía en tu dominio de Railway para CSRF (ajusta el dominio)
#CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if os.getenv("CSRF_TRUSTED_ORIGINS") else []


# Application definition

INSTALLED_APPS = [
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
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

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MONGO_URI = os.getenv("MONGO_URI")

if MONGO_URI:
    try:
        # Timeout bajo para no colgar el arranque, y loguear si falla
        mongoengine.connect(host=MONGO_URI, serverSelectionTimeoutMS=5000, uuidRepresentation="standard")
    except Exception as e:
        logging.warning("No se pudo conectar a MongoDB Atlas al iniciar: %s", e)
else:
    logging.warning("MONGO_URI no está configurada en variables de entorno.")
