import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOCAL_INSTALLED_APPS = ('django_nose', )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

USE_ZOPE_LAYOUT = False

NOSE_ARGS = [
    '--with-coverage',
    '--cover-erase',
    '--cover-package=gemet',
]

try:
    from local_test_settings import *
except ImportError:
    pass
