from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    ThemeFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestGetAvailableLanguages(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['getAvailableLanguages']) + '?'
        self.term = TermFactory()
        self._initialize(self.term, 'prefLabel1', 'definition1', self.english)

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

    def test_invalid_concept_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'concept_uri': 'BAD_CONCEPT_URI'
        }))

    def test_invalid_concept_code(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + '9999'
        }))

    def test_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(self.term, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code
        }))

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(2, len(resp))
        self.assertEqual(resp, [u'en', u'es'])

    def test_two_namespaces(self):
        theme = ThemeFactory(code='1')
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(theme, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code
        }))

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(1, len(resp))
        self.assertEqual(resp, [u'en'])
