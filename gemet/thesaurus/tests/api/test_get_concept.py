from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestGetConcept(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['getConcept']) + '?'
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

    def test_default_language_parameter(self):
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code
        }))
        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(resp.json['preferredLabel']['language'],
                         DEFAULT_LANGCODE)

    def test_invalid_language(self):
        self.assertRaises(
            Fault, self.app.get,
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'language': 'es'
            }))

    def test_invalid_concept_uri(self):
        self.assertRaises(
            Fault, self.app.get,
            self.url + urlencode({'concept_uri': 'BAD_THESAURUS_URI',
                                  'language': self.english.code})
        )

    def test_concept(self):
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
        }))

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel1')
        self.assertEqual(resp['definition']['string'], 'definition1')
        self.assertEqual(resp['uri'], self.ENDPOINT_URI + reverse(
            'concept', args=(self.english.code, self.term.id),
        ))
        self.assertEqual(resp['thesaurus'], self.term.namespace.url)

    def test_language(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(self.term, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            'language': spanish.code,
        }))

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel2')
        self.assertEqual(resp['definition']['string'], 'definition2')
        self.assertEqual(resp['uri'], self.ENDPOINT_URI + reverse(
            'concept', args=(spanish.code, self.term.id)
        ))
        self.assertEqual(resp['thesaurus'], self.term.namespace.url)
