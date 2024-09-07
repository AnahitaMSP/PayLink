"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=config("SECRET_KEY",default='django-insecure-%)kj#qu4+m$ccy4iy6a!brgb-&3*(2&bvfs*fqj6zq!k&z#s4')
DEBUG = config('DEBUG', default=True, cast=bool)

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = config("ALLOWED_HOSTS",cast= lambda v: [item.strip() for item in v.split(',')] ,default="*")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'visits',
    'payments',
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
INTERNAL_IPS = [
    '127.0.0.1',
    # در صورت استفاده از Docker، می‌توانید IP مربوطه را اضافه کنید
]
ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'



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

TIME_ZONE = config('TIME_ZONE',default='UTC')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS=[
    BASE_DIR / 'static'
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/'
AUTH_PASSWORD_VALIDATORS = []

# payment gateway settings
MERCHANT_ID = config("MERCHANT_ID",default="4ced0a1e-4ad8-4309-9668-3ea3ae8e8897")
SANDBOX_MODE = config("SANDBOX_MODE", cast=bool, default=True)

NOVINPAL_API_KEY = "28266702-0fed-4669-9f0a-b70fc7af228a"
NOVINPAL_RETURN_URL = "https://panel.arzdex.shop/payment/verify/"
NOVINPAL_REQUEST_URL = "https://api.novinpal.ir/invoice/request"
NOVINPAL_START_URL = "https://api.novinpal.ir/invoice/start/"
NOVINPAL_VERIFY_URL = "https://api.novinpal.ir/invoice/verify"