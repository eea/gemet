import factory

from gemet.thesaurus.models import (
    Concept, Property, Language, Namespace, Relation, PropertyType, Term,
    Group, SuperGroup, Theme,
)


class NamespaceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Namespace
    FACTORY_DJANGO_GET_OR_CREATE = ('heading',)

    id = 4
    heading = 'Themes'


class LanguageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Language
    FACTORY_DJANGO_GET_OR_CREATE = ('code',)

    code = 'en'
    name = 'English'
    charset = 'utf8_general_ci'


class ConceptFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Concept


class TermFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Term

    id = 1
    code = '1'


class GroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Group

    id = 2
    code = '2'


class SuperGroupFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = SuperGroup

    id = 3
    code = '3'


class ThemeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Theme

    id = 4
    code = '4'


class PropertyFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Property

    concept = factory.SubFactory(ConceptFactory)
    language = factory.SubFactory(LanguageFactory)
    name = 'prefLabel'
    value = 'administration'


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
