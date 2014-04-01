from django.db.models import (
    Model, CharField, ForeignKey, DateTimeField, BooleanField,
)


class Namespace(Model):
    url = CharField(max_length=255)
    heading = CharField(max_length=255)
    version = CharField(max_length=255)
    type_url = CharField(max_length=255)


class Concept(Model):
    namespace = ForeignKey(Namespace)
    concept_code = CharField(max_length=10)
    date_entered = DateTimeField(blank=True, null=True)
    date_changed = DateTimeField(blank=True, null=True)


class Language(Model):
    code = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=255)
    charset = CharField(max_length=100)
    code_alt = CharField(max_length=3)
    direction = CharField(max_length=1, choices=(('0', 'ltr'), ('1', 'rtl')))


class Property(Model):
    concept = ForeignKey(Concept)
    language = ForeignKey(Language)
    name = CharField(max_length=50)
    value = CharField(max_length=65000)
    is_resource = BooleanField(default=False)


class PropertyType(Model):
    label = CharField(max_length=100)
    uri = CharField(max_length=255)


class Relation(Model):
    source = ForeignKey(Concept, related_name='relation_sources')
    target = ForeignKey(Concept, related_name='relation_targets')
    property_type = ForeignKey(PropertyType)


class ForeignRelations(Model):
    concept = ForeignKey(Concept)
    uri = CharField(max_length=512)
    property_type = ForeignKey(PropertyType)
    label = CharField(max_length=100)
    show_in_html = BooleanField(default=True)


class DefinitionSource(Model):
    abbr = CharField(max_length=10, primary_key=True)
    author = CharField(max_length=255)
    title = CharField(max_length=255)
    url = CharField(max_length=255)
    publication = CharField(max_length=255)
    place = CharField(max_length=255)
    year = CharField(max_length=10)
