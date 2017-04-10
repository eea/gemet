from django.contrib import admin

from gemet.thesaurus import models


class ConceptAdmin(admin.ModelAdmin):

    search_fields = ('code',)
    list_display = ('code', 'namespace', 'status', 'version_added')
    list_filter = ('version_added__identifier', 'status')


class ForeignRelationAdmin(admin.ModelAdmin):
    search_fields = ('code',)
    list_display = ('property_type', 'concept', 'version_added', 'status',
                    'label')
    list_filter = ('version_added__identifier', 'status')


class PropertiesAdmin(admin.ModelAdmin):
    search_fields = ('code',)
    list_display = ('name', 'value', 'concept', 'language', 'status',
                    'version_added')
    list_filter = ('version_added__identifier', 'status', 'language', 'name')


class GroupAdmin(ConceptAdmin):
    pass


class SuperGroupAdmin(ConceptAdmin):
    pass


class ThemeAdmin(ConceptAdmin):
    pass


class TermAdmin(ConceptAdmin):
    pass

admin.site.register(models.Namespace)
admin.site.register(models.Concept, ConceptAdmin)
admin.site.register(models.Property, PropertiesAdmin)
admin.site.register(models.Language)
admin.site.register(models.Relation)
admin.site.register(models.ForeignRelation, ForeignRelationAdmin)
admin.site.register(models.Theme, ThemeAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.SuperGroup, SuperGroupAdmin)
admin.site.register(models.Term, ConceptAdmin)
