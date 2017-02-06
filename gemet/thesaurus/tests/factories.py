import factory

from gemet.thesaurus.models import (
    Concept, DefinitionSource, ForeignRelation, Group, InspireTheme, Language,
    Property, PropertyType, Relation, SuperGroup, Term, Theme, Version,
    VersionableModel
)


class VersionFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Version

    identifier = '1.0'
    is_current = True


class ForeignRelationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ForeignRelation

    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class LanguageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Language
    FACTORY_DJANGO_GET_OR_CREATE = ('code',)

    code = 'en'
    name = 'English'
    charset = 'utf8_general_ci'


class ConceptFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Concept

    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class TermFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Term

    id = 1
    code = '1'
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class GroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Group

    id = 2
    code = '2'
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class SuperGroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = SuperGroup

    id = 3
    code = '3'
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class ThemeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Theme

    id = 4
    code = '4'
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class PropertyFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Property

    concept = factory.SubFactory(ConceptFactory)
    language = factory.SubFactory(LanguageFactory)
    version_added = factory.SubFactory(VersionFactory)
    name = 'prefLabel'
    value = 'administration'
    status = VersionableModel.PUBLISHED


class PropertyTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = PropertyType

    id = 1
    name = "themeMember"
    label = "Theme member"


class RelationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Relation

    property_type = factory.SubFactory(PropertyTypeFactory)
    source = factory.SubFactory(ConceptFactory)
    target = factory.SubFactory(ConceptFactory)
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED


class DataSourceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = DefinitionSource


class InspireThemeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = InspireTheme

    id = 5
    code = 'ad'
    version_added = factory.SubFactory(VersionFactory)
    status = VersionableModel.PUBLISHED
