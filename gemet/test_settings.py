import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_ADDR", "db"),
        "NAME": "gemet_test",
        "USER": "gemet",
        "PASSWORD": "gemet",
    }
}

SECRET_KEY = "Test secret key"

LOCAL_INSTALLED_APPS = ("django_nose",)

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

USE_ZOPE_LAYOUT = False

NOSE_ARGS = [
    "--with-coverage",
    "--cover-erase",
    "--cover-package=gemet",
]

USE_ZOPE_LAYOUT = False

ZOPE_URL = "http://www.eionet.europa.eu"
GEMET_URL = ZOPE_URL + "/gemet"

EXPORTS_ROOT = os.path.join(BASE_DIR, "exports-test/")

try:
    from local_test_settings import *
except ImportError:
    pass
