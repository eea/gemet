from django.core.files import File
from django.db.models import Q
from django.test import TestCase, Client

from .factories import VersionFactory, ConceptFactory
from gemet.thesaurus.models import Concept, Import, Property, Namespace


class ConceptImportView(TestCase):

    # Create namespaces, languages, property types, and users
    fixtures = ['data.json']

    def setUp(self):
        version = VersionFactory(identifier='')
        self.client = Client()

        concept_namespace = Namespace.objects.get(heading='Concepts')
        group_namespace = Namespace.objects.get(heading='Groups')
        theme_namespace = Namespace.objects.get(heading='Themes')

        i = 1
        # Create broader concepts
        for value in ['pollution', 'impact source']:
            concept = ConceptFactory(namespace=concept_namespace, code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version
            )
            i += 1

        # Create groups
        for value in ['BIOSPHERE', 'HYDROSPHERE']:
            concept = ConceptFactory(namespace=group_namespace, code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version
            )
            i += 1

        # Create themes
        for value in ['Fake Theme']:
            concept = ConceptFactory(namespace=theme_namespace, code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version
            )
            i += 1

    def test_import_concepts_and_translations_together(self):
        num_concepts_before = Concept.objects.count()
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/concepts.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 45 new concepts were imported
        num_concepts_after = Concept.objects.count()
        self.assertEqual(num_concepts_after - num_concepts_before, 45)
        # Notes are also imported
        self.assertEqual(
            Property.objects.filter(
                name='scopeNote', value='As opposed to green finance'
            ).count(),
            1
        )
        # And multiple altlabels
        self.assertEqual(
            Property.objects.filter(name='altLabel').filter(
                Q(value='altlabel1') | Q(value='altlabel2')
            ).count(),
            2
        )

    def test_import_concepts_and_translations_separately(self):
        num_concepts_before = Concept.objects.count()
        # Import concepts in English first
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/only_en.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 45 new concepts were imported
        num_concepts_after = Concept.objects.count()
        self.assertEqual(num_concepts_after - num_concepts_before, 45)

        num_properties_before = Property.objects.count()
        # Import a separate spreadsheet only with translations
        import_obj = Import.objects.create(
            spreadsheet=File(
                open('gemet/thesaurus/tests/files/only_translations.xlsx')
            )
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # The number of concepts is still the same
        self.assertEqual(Concept.objects.count(), num_concepts_after)
        # New properties were created with translations
        self.assertGreater(Property.objects.count(), num_properties_before)
