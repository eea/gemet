from django.db.models import (
    Model, CharField, ForeignKey, DateTimeField, BooleanField,
)
from django.core.exceptions import ObjectDoesNotExist


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

    @property
    def visible_foreign_relations(self):
        return self.foreign_relations.filter(show_in_html=True)

    def get_property_value(self, property_name, langcode):
        try:
            property_value = self.properties.get(
                name=property_name,
                language__code=langcode,
            ).value
        except ObjectDoesNotExist:
            property_value = None

        return property_value

    def set_attribute(self, property_name, langcode):
        setattr(
            self,
            property_name,
            self.get_property_value(property_name, langcode)
        )

    def set_parent(self, parent_type, langcode):
        parent_name = parent_type + 's'
        setattr(
            self,
            parent_name,
            [r.target.get_property_value('prefLabel', langcode)
             for r in self.source_relations
             .filter(property_type__name=parent_type)]
        )

    def set_children(self):
        if self.namespace.heading in ['Concepts', 'Super groups']:
            self.children = [r.target for r in self.source_relations
                             .filter(property_type__name='narrower')]
        elif self.namespace.heading == 'Groups':
            group_concepts = [r.target for r in self.source_relations
                              .filter(property_type__name='groupMember')]
            self.children = [c for c in group_concepts
                             if not c.source_relations
                             .filter(property_type__name='broader')]
        else:
            self.children = []

    def set_expand(self, expand):
        str_id = str(self.id)
        expand_copy = expand[:]
        if str_id in expand:
            self.expanded = True
            expand_copy.remove(str_id)
        else:
            self.expanded = False
            expand_copy.append(str_id)
        self.expand_param = '-'.join(expand_copy)


class Language(Model):
    code = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=255)
    charset = CharField(max_length=100)
    code_alt = CharField(max_length=3)
    direction = CharField(max_length=1, choices=(('0', 'ltr'), ('1', 'rtl')))

    def __unicode__(self):
        return self.name


class Property(Model):
    concept = ForeignKey(Concept, related_name='properties')
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

    def __unicode__(self):
        return 's: {0}, t: {1}, rel: {2}'.format(
            self.source.code, self.target.code, self.property_type.name)


class ForeignRelation(Model):
    concept = ForeignKey(Concept, related_name='foreign_relations')
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
