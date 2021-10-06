from urllib.parse import urlencode
from xmlrpc.client import Fault

from django.urls import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    GroupFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestFetchGroups(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.url = reverse('api_root', args=['fetchGroups']) + '?'
        self.group = GroupFactory()
        self._initialize(self.group, 'prefLabel1', 'definition1', self.english)

    def _initialize(self, concept, preflabel, definition, lang):
        PropertyFactory(
            concept=concept, name='prefLabel', value=preflabel, language=lang
        )
        PropertyFactory(
            concept=concept, name='definition', value=definition, language=lang
        )

    def _response_valid(self, status, content_type):
        self.assertEqual(200, status)
        self.assertEqual(content_type, 'application/json')

    def test_default_language_parameter(self):
        resp = self.app.get(self.url)
        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(resp.json[0]['preferredLabel']['language'],
                         DEFAULT_LANGCODE)

    def test_invalid_language(self):
        self.assertRaises(Fault, self.app.get,
                          self.url + urlencode({'language': 'es'}))
