from django.contrib import admin
from .models import Namespace, Concept, Property, Language

admin.site.register(Namespace)
admin.site.register(Concept)
admin.site.register(Property)
admin.site.register(Language)
