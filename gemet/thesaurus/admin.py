from django.contrib import admin

from gemet.thesaurus import models


admin.site.register(models.Namespace)
admin.site.register(models.Concept)
admin.site.register(models.Property)
admin.site.register(models.Language)
admin.site.register(models.Relation)
admin.site.register(models.ForeignRelation)
admin.site.register(models.Theme)
admin.site.register(models.Group)
admin.site.register(models.SuperGroup)
admin.site.register(models.Term)
