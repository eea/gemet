from django.core.urlresolvers import reverse
from django.db import models

from gemet.thesaurus import NS_VIEW_MAPPING


class Version(models.Model):
    identifier = models.CharField(max_length=255)
    publication_date = models.DateTimeField(blank=True, null=True)
    changed_note = models.TextField()
    is_current = models.BooleanField(default=False)


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
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=PENDING)
    version_added = models.ForeignKey(Version)

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

    @property
    def visible_foreign_relations(self):
        result = {}
        relations = self.foreign_relations.filter(show_in_html=True)
        for relation in relations:
            (
                result.setdefault(relation.property_type.label, [])
                .append(relation)
            )
        return result

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
            if prop['name'] == 'altLabel':
                if hasattr(self, 'alternatives'):
                    self.alternatives.append(prop['value'])
                else:
                    self.alternatives = [prop['value']]
            else:
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
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'concept__code', 'name')
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
            .values('id', 'concept__code', 'name')
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

    @property
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
    base_manager = models.Manager()


class Theme(Concept):
    siblings_relations = ['themeMember']

    class Meta:
        proxy = True

    objects = ConceptManager('Themes')
    base_manager = models.Manager()


class Group(Concept):
    siblings_relations = ['broader', 'groupMember']

    class Meta:
        proxy = True

    objects = ConceptManager('Groups')
    base_manager = models.Manager()


class SuperGroup(Concept):
    siblings_relations = ['narrower']

    class Meta:
        proxy = True

    objects = ConceptManager('Super groups')
    base_manager = models.Manager()


class InspireTheme(Concept):
    siblings_relations = []

    class Meta:
        proxy = True

    objects = ConceptManager('Inspire Themes')
    base_manager = models.Manager()
