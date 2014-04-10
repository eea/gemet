from django.contrib import admin
from .models import Namespace, Concept, Property, Language, Relation

admin.site.register(Namespace)
admin.site.register(Concept)
admin.site.register(Property)
admin.site.register(Language)
admin.site.register(Relation)
