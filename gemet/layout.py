import requests
from django.conf import settings


def layout_context_processor(request):
    return {"layout_template": "layout.html"}
