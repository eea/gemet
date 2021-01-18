from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import mark_safe

from gemet.thesaurus import PENDING, PUBLISHED, DELETED, DELETED_PENDING
from gemet.thesaurus import NS_VIEW_MAPPING, RELATION_PAIRS
from gemet.thesaurus import SEARCH_FIELDS, SEARCH_SEPARATOR


class TimeTrackedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Version(models.Model):
    identifier = models.CharField(max_length=255)
    publication_date = models.DateTimeField(blank=True, null=True)
    change_note = models.TextField()
    is_current = models.BooleanField(default=False)

    @staticmethod
    def under_work():
        return Version.objects.get(identifier="")

    def __unicode__(self):
        if self.identifier == "":
            return 'Upcoming version'
        return self.identifier


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super(PublishedManager, self).get_queryset()
            .filter(status__in=VersionableModel.PUBLISHED_STATUS_OPTIONS)
        )


class AuthorizedUser(models.Model):
    username = models.CharField(max_length=100)

    @staticmethod
    def get_authorized_users():
        return AuthorizedUser.objects.values_list('username', flat=True)


class VersionableModel(models.Model):
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


class Concept(VersionableModel, TimeTrackedModel):
    namespace = models.ForeignKey(Namespace)
    code = models.CharField(max_length=10)
    # TODO: Rename to created_at/updated_at and use auto_now and auto_now_add

    EDITABLE = False
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

    @cached_property
    def name(self):
        """ Relies on data being set properly on set_attributes """
        return getattr(self, 'prefLabel', '')

    @cached_property
    def label(self):
        """ Calculates and return prefLabel value of the Concept in English """
        return self.properties.filter(
            language='en', name='prefLabel', status__in=[0, 1]
        ).first().value

    def inherit_groups_and_themes_from_broader(self, version=None):
        """
        Inherit groups and themes from broader concepts.
        Returns the number of relations created.
        """
        version = version or Version.under_work()
        broader_concepts = Term.objects.filter(
            target_relations__source=self,
            target_relations__property_type__name='broader'
        )
        num_created = 0
        for broader in broader_concepts:
            group_theme_relations = broader.source_relations.filter(
                property_type__name__in=['group', 'theme']
            )

            for relation in group_theme_relations:
                relation, created = Relation.objects.get_or_create(
                    source=self,  # child
                    target=relation.target,  # parent
                    property_type=relation.property_type,
                    defaults={'version_added': version, 'status': PENDING}
                )
                if created:
                    num_created += 1
        return num_created

    def update_or_create_properties(
        self, property_values, language_id='en', version=None
    ):
        version = version or Version.under_work()

        # Soft delete matching published properties
        self.properties.filter(
            name__in=property_values.keys(),
            language_id=language_id,
            status=PUBLISHED
        ).update(status=DELETED_PENDING)

        # For each property
        for name, value in property_values.iteritems():
            if value:
                if name == 'altLabel':
                    # altLabel key maps to multiple values
                    assert isinstance(value, list)
                    # Delete existing
                    self.properties.filter(
                        name='altLabel',
                        language_id=language_id,
                        status=PENDING
                    ).delete()
                    for alt_label in value:
                        # And create new ones
                        self.properties.create(
                            status=PENDING,
                            version_added=version,
                            language_id=language_id,
                            name=name,
                            value=alt_label,
                        )
                else:
                    # Update pending if exists
                    matches = self.properties.filter(
                        language_id=language_id,
                        name=name,
                        status=PENDING
                    ).update(value=value)
                    if not matches:
                        # If it doesn't exist, create it
                        self.properties.create(
                            status=PENDING,
                            version_added=version,
                            language_id=language_id,
                            name=name,
                            value=value,
                        )
        self.update_or_create_search_text(language_id, version)

    def update_or_create_search_text(self, language_code, version=None):
        """
        Update or create Property of type searchText, an internal type of
        property consisting of the concatenated values of all searchable
        properties of a concept.
        """
        version = version or Version.under_work()

        # Get values from searchable properties
        search_prop_values = self.properties.filter(
            language_id=language_code,
            name__in=SEARCH_FIELDS,
            status__in=[PUBLISHED, PENDING],
        ).values_list('value', flat=True)

        # Concatenate them using internal format
        if search_prop_values:
            search_text = SEARCH_SEPARATOR.join(search_prop_values)
            search_text = SEARCH_SEPARATOR + search_text + SEARCH_SEPARATOR
        else:
            search_text = ''

        # Look for existing searchText Property object
        search_text_property = self.properties.filter(
            language_id=language_code,
            name='searchText',
            status__in=[PUBLISHED, PENDING],
        ).first()

        if search_text_property:
            # If it exists, update it with the new calculated value
            search_text_property.value = search_text
            search_text_property.save()
        else:
            # If not, create it
            search_text_property = self.properties.create(
                language_id=language_code,
                name='searchText',
                status=PENDING,
                version_added=version,
            )

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

    def get_siblings(self, langcode, relation_type):
        values = ['id', 'concept__code', 'name']
        values.extend(self.extra_values)
        property_status = getattr(self, 'property_status', self.status_list)
        return (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                status__in=property_status,
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

    def set_parents(self, langcode):
        for parent_type in self.parents_relations:
            parent_name = parent_type + 's'
            setattr(self, parent_name,
                    self.get_siblings(langcode, parent_type))

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
                    .filter(
                        property_type__name='groupMember',
                        status__in=self.status_list,
                    )
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
        try:
            return u"{} ({})".format(self.label, self.code)
        except Exception:
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

    @property
    def namespace(self):
        namespaces = {
            'broader': Namespace.objects.get(heading='Concepts'),
            'group': Namespace.objects.get(heading='Groups'),
            'theme': Namespace.objects.get(heading='Themes'),
        }
        return namespaces.get(self.name)

    def __unicode__(self):
        return self.name


class Relation(VersionableModel):
    source = models.ForeignKey(  # child
        Concept, related_name='source_relations'
    )
    target = models.ForeignKey(  # parent
        Concept, related_name='target_relations'
    )
    property_type = models.ForeignKey(PropertyType)

    def __unicode__(self):
        return 's: {0}, t: {1}, rel: {2}'.format(
            self.source.code, self.target.code, self.property_type.name)

    @cached_property
    def reverse(self):
        return (
            Relation.objects
            .filter(source=self.target, target=self.source)
            .first()
        )

    def create_reverse(self):
        reverse_relation_name = RELATION_PAIRS[self.property_type.name]
        reverse_relation = PropertyType.objects.get(name=reverse_relation_name)
        return Relation.objects.create(
            source=self.target,
            target=self.source,
            property_type=reverse_relation,
            status=self.status,
            version_added=self.version_added,
        )


class ForeignRelation(VersionableModel):
    concept = models.ForeignKey(Concept, related_name='foreign_relations')
    uri = models.CharField(max_length=512)
    property_type = models.ForeignKey(PropertyType)
    label = models.CharField(max_length=100)
    show_in_html = models.BooleanField(default=True)


class DefinitionSource(models.Model):
    abbr = models.CharField(max_length=10, primary_key=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    publication = models.CharField(max_length=255, null=True, blank=True)
    place = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)


class AsyncTask(models.Model):
    QUEUED = u'queued'
    FINISHED = u'finished'
    FAILED = u'failed'
    STARTED = u'started'

    STATUS = (
        (QUEUED, 'Queued'),
        (FINISHED, 'Finished'),
        (FAILED, 'Failed'),
        (STARTED, 'Started'),
    )

    task = models.CharField(max_length=32)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS, default=QUEUED)
    user = models.ForeignKey(User)
    version = models.OneToOneField(
        Version,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class Import(TimeTrackedModel):
    """
    Keeps track of data imports via excel files.
    """
    spreadsheet = models.FileField(
        upload_to='imports/',
        help_text=mark_safe(
            'Details about the supported file format can be found <a href="'
            'https://taskman.eionet.europa.eu/projects/infrastructure/wiki/'
            'Importing_new_concepts_in_GEMET">here</a>.'
        )
    )
    started_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
    succeeded_at = models.DateTimeField(null=True)
    logs = models.TextField(blank=True)

    @property
    def status(self):
        if not self.started_at:
            return u'Unstarted'
        elif self.succeeded_at:
            return u'Succeeded'
        elif self.failed_at:
            return u'Failed'
        else:
            return u'In progress'

    def run(self):
        self.logs = ''
        self.failed_at = None
        self.succeeded_at = None
        self.started_at = timezone.now()
        self.save()

        try:
            from gemet.thesaurus.import_spreadsheet import Importer
            importer = Importer(self)
            self.logs = importer.import_file()
            self.succeeded_at = timezone.now()
            self.save()
        except Exception as exc:
            self.logs = str(exc)
            self.failed_at = timezone.now()
            self.save()
            raise


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

    def get_by_name(self, name):
        return self.get_queryset().filter(
            properties__name='prefLabel', properties__value=name,
            properties__language_id='en'
        ).distinct().get()


class PublishedConceptManager(ConceptManager):
    def get_queryset(self):
        return (
            super(PublishedConceptManager, self).get_queryset()
            .filter(status__in=[PUBLISHED, DELETED_PENDING])
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


class EditMixin(object):
    status_list = [PUBLISHED, PENDING, DELETED_PENDING]
    EDITABLE = True
    extra_values = ['status']
    property_status = [PUBLISHED, PENDING]

    def name(self):
        pref_label = getattr(self, 'prefLabel', [])
        for item in pref_label:
            if item['editable']:
                return item['value']

    def set_attributes(self, langcode, property_list):
        properties = self.get_attributes(langcode, property_list)
        for prop in properties:
            prop['editable'] = prop['status'] in (PUBLISHED, PENDING)
            value = getattr(self, prop['name'], [])
            value.append(prop)
            setattr(self, prop['name'], value)

    def set_parents(self, langcode):
        for parent_relation in self.parents_relations:
            parents = self.get_siblings(langcode, parent_relation)
            for parent in parents:
                parent['status'] = self.source_relations.filter(
                    target_id=parent['id']).first().status
            setattr(self, parent_relation + 's', parents)

    def set_siblings(self, langcode):
        for relation_type in self.siblings_relations:
            siblings = self.get_siblings(langcode, relation_type)
            for sibling in siblings:
                sibling['status'] = self.source_relations.filter(
                    target_id=sibling['id']).first().status
            setattr(self, relation_type + '_concepts', siblings)


class EditableTheme(EditMixin, Theme):

    class Meta:
        proxy = True


class EditableTerm(EditMixin, Term):

    class Meta:
        proxy = True


class EditableGroup(EditMixin, Group):

    class Meta:
        proxy = True


class EditableSuperGroup(EditMixin, SuperGroup):

    class Meta:
        proxy = True
