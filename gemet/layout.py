import requests
from django.conf import settings


def layout_context_processor(request):
    if settings.USE_ZOPE_LAYOUT:
        return {'layout_template': 'layout_zope.html'}
    else:
        return {'layout_template': 'layout.html'}
