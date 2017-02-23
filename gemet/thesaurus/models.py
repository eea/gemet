from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property

from gemet.thesaurus import NS_VIEW_MAPPING

RELATION_TYPES = [
    'theme',
    'group',
    'broader',
    'narrower',
    'related',
]

FOREIGN_RELATION_TYPES = [
    'exactMatch',
    'broadMatch',
    'closeMatch',
    'narrowMatch',
    'relatedMatch',
    'hasWikipediaArticle',
    'sameEEAGlossary',
    'seeAlso',
]


class Version(models.Model):
    identifier = models.CharField(max_length=255)
    publication_date = models.DateTimeField(blank=True, null=True)
    changed_note = models.TextField()
    is_current = models.BooleanField(default=False)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super(PublishedManager, self).get_queryset()
            .filter(status__in=VersionableModel.PUBLISHED_STATUS_OPTIONS)
        )


class VersionableModel(models.Model):
    PENDING = 0
    PUBLISHED = 1
    DELETED = 2
    DELETED_PENDING = 3
    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (PUBLISHED, 'published'),
        (DELETED, 'deleted'),
        (DELETED_PENDING, 'deleted pending'),
    )
    PUBLISHED_STATUS_OPTIONS = [PUBLISHED, DELETED_PENDING]
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=PENDING)
    version_added = models.ForeignKey(Version)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        abstract = True


class Namespace(models.Model):
    url = models.CharField(max_length=255)
    heading = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    type_url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.heading


class Concept(VersionableModel):
    namespace = models.ForeignKey(Namespace)
    code = models.CharField(max_length=10)
    date_entered = models.DateTimeField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)

    parents_relations = []
    status_list = VersionableModel.PUBLISHED_STATUS_OPTIONS
    extra_values = []

    @cached_property
    def visible_foreign_relations(self):
        values = ['id', 'label', 'uri', 'property_type__label']
        values.extend(self.extra_values)
        return (
            self.foreign_relations
            .filter(
                show_in_html=True,
                status__in=self.status_list,
            )
            .values(*values)
            .order_by('property_type__label')
        )

    @property
    def name(self):
        return getattr(self, 'prefLabel', '')

    def get_attributes(self, langcode, property_list):
        values = ['id', 'name', 'value']
        values.extend(self.extra_values)
        return (
            self.properties
            .filter(
                name__in=property_list,
                language__code=langcode,
                status__in=self.status_list,
            )
            .values(*values)
        )

    def set_attributes(self, langcode, property_list):
        properties = self.get_attributes(langcode, property_list)
        if not hasattr(self, 'alternatives'):
            self.alternatives = []
        for prop in properties:
            if prop['name'] == 'altLabel':
                self.alternatives.append(prop['value'])
            else:
                setattr(self, prop['name'], prop['value'])

    def set_parents(self, langcode):
        values = ['id', 'name']
        values.extend(self.extra_values)
        for parent_type in self.parents_relations:
            parent_name = parent_type + 's'
            setattr(
                self,
                parent_name,
                Property.objects.filter(
                    name='prefLabel',
                    language__code=langcode,
                    concept_id__in=self.source_relations
                    .filter(
                        property_type__name=parent_type,
                        status__in=self.status_list,
                    )
                    .values_list('target_id', flat=True)
                )
                .extra(select={'name': 'value',
                               'id': 'concept_id'},
                       order_by=['name'])
                .values(*values)
            )

    def get_siblings(self, langcode, relation_type):
        values = ['id', 'concept__code', 'name']
        values.extend(self.extra_values)
        return (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                concept_id__in=(
                    self.source_relations
                    .filter(
                        property_type__name=relation_type,
                        status__in=self.status_list,
                    )
                    .values_list('target_id', flat=True)
                )
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values(*values)
        )

    def set_siblings(self, langcode):
        for relation_type in self.siblings_relations:
            setattr(self, relation_type + '_concepts',
                    self.get_siblings(langcode, relation_type))

    def get_children(self, langcode):
        values = ['id', 'concept__code', 'name']
        values.extend(self.extra_values)

        children = (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                status__in=self.status_list,
            )
        )

        if self.namespace.heading in ['Concepts', 'Super groups']:
            children = children.filter(
                concept_id__in=(
                    self.source_relations
                    .filter(
                        property_type__name='narrower',
                        status__in=self.status_list,
                    )
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
                            status__in=self.status_list,
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
                    .filter(
                        property_type__name='themeMember',
                        status__in=self.status_list,
                    )
                    .values_list('target_id', flat=True)
                )
            )

        return (
            children
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values(*values)
        )

    def get_concept_type(self):
        return NS_VIEW_MAPPING.get(self.namespace.heading, 'concept')

    def get_about_url(self):
        # get the concept type, since we cannot rely on self.concept_type
        concept_type = self.get_concept_type()
        if concept_type == 'inspire_theme':
            return self.namespace.url + self.code
        return reverse('concept_redirect',
                       kwargs={'concept_type': concept_type,
                               'concept_code': self.code})

    def __unicode__(self):
        return self.code


class Language(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    charset = models.CharField(max_length=100)
    code_alt = models.CharField(max_length=3)
    direction = models.CharField(max_length=1,
                                 choices=(('0', 'ltr'), ('1', 'rtl')))

    @property
    def rtl(self):
        return self.direction == '1'

    def __unicode__(self):
        return self.name


class Property(VersionableModel):
    concept = models.ForeignKey(Concept, related_name='properties')
    language = models.ForeignKey(Language, related_name='properties')
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=16000)
    is_resource = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "properties"

    @cached_property
    def property_type(self):
        return PropertyType.get_by_name(self.name)

    def __unicode__(self):
        return "{0} - {1} ({2})".format(
            self.concept.code, self.name, self.language.code)


class PropertyType(models.Model):
    name = models.CharField(max_length=40)
    label = models.CharField(max_length=100)
    uri = models.CharField(max_length=255)

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


class Relation(VersionableModel):
    source = models.ForeignKey(Concept, related_name='source_relations')
    target = models.ForeignKey(Concept, related_name='target_relations')
    property_type = models.ForeignKey(PropertyType)

    def __unicode__(self):
        return 's: {0}, t: {1}, rel: {2}'.format(
            self.source.code, self.target.code, self.property_type.name)


class ForeignRelation(VersionableModel):
    concept = models.ForeignKey(Concept, related_name='foreign_relations')
    uri = models.CharField(max_length=512)
    property_type = models.ForeignKey(PropertyType)
    label = models.CharField(max_length=100)
    show_in_html = models.BooleanField(default=True)


class DefinitionSource(models.Model):
    abbr = models.CharField(max_length=10, primary_key=True)
    author = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    publication = models.CharField(max_length=255, null=True)
    place = models.CharField(max_length=255, null=True)
    year = models.CharField(max_length=10, null=True)


class ConceptManager(models.Manager):

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
        return super(ConceptManager, self).get_queryset().filter(namespace=ns)

    def create(self, **kwargs):
        ns = self.get_ns()
        kwargs.setdefault('namespace', ns)
        return super(ConceptManager, self).create(**kwargs)


class PublishedConceptManager(ConceptManager):
    def get_queryset(self):
        return (
            super(PublishedConceptManager, self).get_queryset()
            .filter(status__in=[
                VersionableModel.PUBLISHED, VersionableModel.DELETED_PENDING])
        )


class Term(Concept):
    siblings_relations = ['broader', 'narrower', 'related']
    parents_relations = ['group', 'theme']
    NAMESPACE = 'Concepts'

    class Meta:
        proxy = True

    objects = ConceptManager(NAMESPACE)
    published = PublishedConceptManager(NAMESPACE)


class Theme(Concept):
    siblings_relations = ['themeMember']
    NAMESPACE = 'Themes'

    class Meta:
        proxy = True

    objects = ConceptManager(NAMESPACE)
    published = PublishedConceptManager(NAMESPACE)


class Group(Concept):
    siblings_relations = ['broader', 'groupMember']
    NAMESPACE = 'Groups'

    class Meta:
        proxy = True

    objects = ConceptManager(NAMESPACE)
    published = PublishedConceptManager(NAMESPACE)


class SuperGroup(Concept):
    siblings_relations = ['narrower']
    NAMESPACE = 'Super groups'

    class Meta:
        proxy = True

    objects = ConceptManager(NAMESPACE)
    published = PublishedConceptManager(NAMESPACE)


class InspireTheme(Concept):
    siblings_relations = []
    NAMESPACE = 'Inspire Themes'

    class Meta:
        proxy = True

    objects = ConceptManager(NAMESPACE)
    published = PublishedConceptManager(NAMESPACE)


class EditableTerm(Term):
    status_list = [Term.PUBLISHED, Term.PENDING, Term.DELETED_PENDING]
    extra_values = ['status']

    class Meta:
        proxy = True

    def name(self):
        pref_label = getattr(self, 'prefLabel', [])
        for item in pref_label:
            if item['editable']:
                return item['value']

    def set_attributes(self, langcode, property_list):
        properties = self.get_attributes(langcode, property_list)
        for prop in properties:
            prop['editable'] = prop['status'] in (self.PUBLISHED, self.PENDING)
            value = getattr(self, prop['name'], [])
            value.append(prop)
            setattr(self, prop['name'], value)

    def set_parents(self, langcode):
        super(EditableTerm, self).set_parents(langcode)
        # This is ugly; TODO refactor
        for theme in self.themes:
            theme['status'] = self.source_relations.filter(
                target_id=theme['id']).first().status
        for group in self.groups:
            group['status'] = self.source_relations.filter(
                target_id=group['id']).first().status
