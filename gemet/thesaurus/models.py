from django.db.models import (
    Model, CharField, ForeignKey, DateTimeField, BooleanField,
)


class Namespace(Model):
    url = CharField(max_length=255)
    heading = CharField(max_length=255)
    version = CharField(max_length=255)
    type_url = CharField(max_length=255)

    def __unicode__(self):
        return self.heading


class Concept(Model):
    namespace = ForeignKey(Namespace)
    code = CharField(max_length=10)
    date_entered = DateTimeField(blank=True, null=True)
    date_changed = DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.code


class Language(Model):
    code = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=255)
    charset = CharField(max_length=100)
    code_alt = CharField(max_length=3)
    direction = CharField(max_length=1, choices=(('0', 'ltr'), ('1', 'rtl')))

    def __unicode__(self):
        return self.name


class Property(Model):
    concept = ForeignKey(Concept)
    language = ForeignKey(Language)
    name = CharField(max_length=50)
    value = CharField(max_length=65000)
    is_resource = BooleanField(default=False)

    def __unicode__(self):
        return "{0} - {1} ({2})".format(
            self.concept.code, self.name, self.language.code)

    class Meta:
        verbose_name_plural = "properties"


class PropertyType(Model):
    name = CharField(max_length=40)
    label = CharField(max_length=100)
    uri = CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Relation(Model):
    source = ForeignKey(Concept, related_name='source_relations')
    target = ForeignKey(Concept, related_name='target_relations')
    property_type = ForeignKey(PropertyType)


class ForeignRelation(Model):
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
