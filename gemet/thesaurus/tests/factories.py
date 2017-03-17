import factory

from gemet.thesaurus import PUBLISHED
from gemet.thesaurus.models import (
    Concept, DefinitionSource, ForeignRelation, Group, InspireTheme, Language,
    Property, PropertyType, Relation, SuperGroup, Term, Theme, Version,
)


class VersionFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Version
    FACTORY_DJANGO_GET_OR_CREATE = ('identifier',)

    identifier = '1.0'
    is_current = True


class LanguageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Language
    FACTORY_DJANGO_GET_OR_CREATE = ('code',)

    code = 'en'
    name = 'English'
    charset = 'utf8_general_ci'


class ConceptFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Concept

    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class TermFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Term

    code = '1'
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class GroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Group

    code = '2'
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class SuperGroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = SuperGroup

    code = '3'
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class ThemeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Theme

    code = '4'
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class PropertyFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Property

    concept = factory.SubFactory(TermFactory)
    language = factory.SubFactory(LanguageFactory)
    version_added = factory.SubFactory(VersionFactory)
    name = 'prefLabel'
    value = 'administration'
    status = PUBLISHED


class PropertyTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = PropertyType

    name = "themeMember"
    label = "Theme member"


class RelationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Relation

    property_type = factory.SubFactory(PropertyTypeFactory)
    source = factory.SubFactory(TermFactory)
    target = factory.SubFactory(ThemeFactory)
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class ForeignRelationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ForeignRelation

    property_type = factory.SubFactory(PropertyTypeFactory)
    concept = factory.SubFactory(TermFactory)
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED


class DataSourceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = DefinitionSource


class InspireThemeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = InspireTheme

    code = 'ad'
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED
