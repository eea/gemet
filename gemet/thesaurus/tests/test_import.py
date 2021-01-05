from django.core.files import File
from django.test import TestCase, Client

from .factories import VersionFactory
from gemet.thesaurus.models import Concept, Import


class ConceptImportView(TestCase):

    # Create namespaces, languages, property types, and users
    fixtures = ['data.json']

    def setUp(self):
        VersionFactory(identifier='')
        self.client = Client()

    def test_import(self):
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
