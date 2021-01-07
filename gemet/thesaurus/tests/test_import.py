from django.core.files import File
from django.test import TestCase, Client

from .factories import VersionFactory
from gemet.thesaurus.models import Concept, Import, Property


class ConceptImportView(TestCase):

    # Create namespaces, languages, property types, and users
    fixtures = ['data.json']

    def setUp(self):
        VersionFactory(identifier='')
        self.client = Client()

    def test_import_concepts_and_translations_together(self):
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/concepts.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Concept.objects.filter(
                status=0, namespace__heading='Concepts'
            ).count(),
            79
        )
        self.assertEqual(
            Concept.objects.filter(
                status=0, namespace__heading='Groups'
            ).count(),
            2
        )
        # Notes are also imported
        self.assertEqual(
            Property.objects.filter(
                name='scopeNote', value='As opposed to green finance'
            ).count(),
            1
        )

    def test_import_concepts_and_translations_separately(self):
        # Import concepts in English first
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/only_en.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Concept.objects.filter(
                status=0, namespace__heading='Concepts'
            ).count(),
            79
        )
        self.assertEqual(
            Concept.objects.filter(
                status=0, namespace__heading='Groups'
            ).count(),
            2
        )
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
        self.assertEqual(Concept.objects.filter(status=0).count(), 81)
        # New properties were created with translations
        self.assertGreater(Property.objects.count(), num_properties_before)
