from django.contrib import admin
from .models import (
    Namespace,
    Concept,
    Property,
    Language,
    Relation,
    ForeignRelation,
    Theme,
    Group,
    Term,
    SuperGroup,
)

admin.site.register(Namespace)
admin.site.register(Concept)
admin.site.register(Property)
admin.site.register(Language)
admin.site.register(Relation)
admin.site.register(ForeignRelation)
admin.site.register(Theme)
admin.site.register(Group)
admin.site.register(SuperGroup)
admin.site.register(Term)
