from django.core.urlresolvers import reverse
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    DateTimeField,
    BooleanField,
    Manager,
)

from gemet.thesaurus import NS_VIEW_MAPPING


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

    parents_relations = []

    @property
    def visible_foreign_relations(self):
        return self.foreign_relations.filter(show_in_html=True)

    @property
    def name(self):
        return getattr(self, 'prefLabel', '')

    def set_attributes(self, langcode, property_list):
        properties = (
            self.properties.filter(
                name__in=property_list,
                language__code=langcode,
            )
            .values('name', 'value')
        )
        for prop in properties:
            setattr(self, prop['name'], prop['value'])

    def set_parents(self, langcode):
        for parent_type in self.parents_relations:
            parent_name = parent_type + 's'
            setattr(
                self,
                parent_name,
                Property.objects.filter(
                    name='prefLabel',
                    language__code=langcode,
                    concept_id__in=self.source_relations
                    .filter(property_type__name=parent_type)
                    .values_list('target_id', flat=True)
                )
                .extra(select={'name': 'value',
                               'id': 'concept_id'},
                       order_by=['name'])
                .values('id', 'name')
            )

    def get_siblings(self, langcode, relation_type):
        return (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                concept_id__in=(
                    self.source_relations
                    .filter(property_type__name=relation_type)
                    .values_list('target_id', flat=True)
                )
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

    def set_siblings(self, langcode):
        for relation_type in self.siblings_relations:
            setattr(self, relation_type + '_concepts',
                    self.get_siblings(langcode, relation_type))

    def get_children(self, langcode):
        children = (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
            )
        )

        if self.namespace.heading in ['Concepts', 'Super groups']:
            children = children.filter(
                concept_id__in=(
                    self.source_relations
                    .filter(property_type__name='narrower')
                    .values_list('target_id', flat=True)
                )
            )
        elif self.namespace.heading == 'Groups':
            children = children.filter(
                concept_id__in=(
                    self.source_relations
                    .filter(property_type__name='groupMember')
                    .exclude(
                        target__id__in=Relation.objects.filter(
                            property_type__name='broader',
                        )
                        .values_list('source_id', flat=True)
                    )
                    .values_list('target_id', flat=True)
                )
            )
        elif self.namespace.heading == 'Themes':
            children = children.filter(
                concept_id__in=(
                    self.source_relations
                    .filter(property_type__name='themeMember')
                    .values_list('target_id', flat=True)
                )
            )

        return (
            children
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

    def get_concept_type(self):
        return NS_VIEW_MAPPING.get(self.namespace.heading, 'concept')

    def get_about_url(self):
        # get the concept type, since we cannot rely on self.concept_type
        concept_type = self.get_concept_type()
        if concept_type == 'inspire-theme':
            return self.namespace.url + self.code
        return reverse('concept_redirect',
                       kwargs={'concept_type': concept_type,
                               'concept_code': self.code})

    def __unicode__(self):
        return self.code


class Language(Model):
    code = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=255)
    charset = CharField(max_length=100)
    code_alt = CharField(max_length=3)
    direction = CharField(max_length=1, choices=(('0', 'ltr'), ('1', 'rtl')))

    @property
    def rtl(self):
        return self.direction == '1'

    def __unicode__(self):
        return self.name


class Property(Model):
    concept = ForeignKey(Concept, related_name='properties')
    language = ForeignKey(Language, related_name='properties')
    name = CharField(max_length=50)
    value = CharField(max_length=16000)
    is_resource = BooleanField(default=False)

    class Meta:
        verbose_name_plural = "properties"

    @property
    def property_type(self):
        return PropertyType.get_by_name(self.name)

    def __unicode__(self):
        return "{0} - {1} ({2})".format(
            self.concept.code, self.name, self.language.code)


class PropertyType(Model):
    name = CharField(max_length=40)
    label = CharField(max_length=100)
    uri = CharField(max_length=255)

    @property
    def prefix(self):
        uri = self.uri
        uri = uri[uri.rfind('/') + 1:]
        if '#' not in uri:
            return ''
        schema, suffix = uri.split('#')
        if schema == 'core':
            return 'skos:' + suffix
        return 'gemet:' + suffix

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.filter(name=name).first()

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
    author = CharField(max_length=255, null=True)
    title = CharField(max_length=255, null=True)
    url = CharField(max_length=255, null=True)
    publication = CharField(max_length=255, null=True)
    place = CharField(max_length=255, null=True)
    year = CharField(max_length=10, null=True)


class ConceptManager(Manager):

    def __init__(self, namespace):
        self.namespace = namespace
        self.ns = None
        super(ConceptManager, self).__init__()

    def get_ns(self):
        if self.ns is None:
            self.ns = Namespace.objects.get(heading=self.namespace)
        return self.ns

    def get_queryset(self):
        ns = self.get_ns()
        return self.model.base_manager.filter(namespace=ns)

    def create(self, **kwargs):
        ns = self.get_ns()
        kwargs.setdefault('namespace', ns)
        return super(ConceptManager, self).create(**kwargs)


class Term(Concept):
    siblings_relations = ['broader', 'narrower', 'related']
    parents_relations = ['group', 'theme']

    class Meta:
        proxy = True

    objects = ConceptManager('Concepts')
    base_manager = Manager()


class Theme(Concept):
    siblings_relations = ['themeMember']

    class Meta:
        proxy = True

    objects = ConceptManager('Themes')
    base_manager = Manager()


class Group(Concept):
    siblings_relations = ['broader', 'groupMember']

    class Meta:
        proxy = True

    objects = ConceptManager('Groups')
    base_manager = Manager()


class SuperGroup(Concept):
    siblings_relations = ['narrower']

    class Meta:
        proxy = True

    objects = ConceptManager('Super groups')
    base_manager = Manager()


class InspireTheme(Concept):
    siblings_relations = []

    class Meta:
        proxy = True

    objects = ConceptManager('Inspire Themes')
    base_manager = Manager()
