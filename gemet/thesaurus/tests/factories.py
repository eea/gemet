import factory

from gemet.thesaurus.models import (
    Concept, Property, Language, Namespace, Relation, PropertyType
)


class NamespaceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Namespace

    id = 4
    heading = 'Themes'


class LanguageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Language

    code = 'en'
    name = 'English'


class ConceptFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Concept

    id = 1
    code = '1'
    namespace_id = 4


class PropertyFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Property

    concept_id = 1
    language_id = 'en'
    name = 'prefLabel'
    value = 'administration'


class RelationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Relation

    source_id = 1
    target_id = 2
    property_type_id = 1


class PropertyTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = PropertyType

    id = 1
    name = "themeMember"
    label = "Theme member"
