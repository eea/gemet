import factory

from gemet.thesaurus.models import Concept, Property


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
