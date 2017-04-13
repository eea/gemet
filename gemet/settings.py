"""
Django settings for gemet project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*e59o%%4$uxue*-aqn58$adv!fu+%p&7rg3bp=k36blzn9#(4r'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gemet.thesaurus',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gemet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'gemet.layout.layout_context_processor',
                'gemet.thesaurus.context_processors.globals',
            ],
        },
    },
]


WSGI_APPLICATION = 'gemet.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

USE_ZOPE_LAYOUT = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static/')
STATIC_URL = '/static/'

# Exports / Downloads

EXPORTS_ROOT = os.path.join(BASE_DIR, 'exports/')
EXPORTS_URL = '/exports/'

# Authentication
# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


LOCAL_INSTALLED_APPS = ()
try:
    from local_settings import *
    INSTALLED_APPS += LOCAL_INSTALLED_APPS
    MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
except ImportError:
    pass

if 'test' in sys.argv:
    try:
        from test_settings import *
        INSTALLED_APPS += LOCAL_INSTALLED_APPS
    except ImportError:
        pass
