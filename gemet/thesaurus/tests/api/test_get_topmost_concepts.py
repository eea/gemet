from urllib.parse import urlencode
from xmlrpc.client import Fault

from django.urls import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    ThemeFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestGetTopmostConcepts(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['getTopmostConcepts']) + '?'
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
        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url})
        )
        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(resp.json.pop()['preferredLabel']['language'],
                         DEFAULT_LANGCODE)

    def test_invalid_language(self):
        self.assertRaises(
            Fault, self.app.get,
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url,
                                  'language': 'es'})
        )

    def test_invalid_thesaurus_uri(self):
        self.assertRaises(
            Fault, self.app.get,
            self.url + urlencode({'thesaurus_uri': 'BAD_THESAURUS_URI',
                                  'language': self.english.code})
        )

    def test_missing_thesaurus_uri(self):
        self.assertRaises(
            Fault, self.app.get,
            self.url + urlencode({'language': self.english.code})
        )

    def test_one_term(self):
        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url})
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel1')
        self.assertEqual(resp['preferredLabel']['language'], 'en')
        self.assertEqual(resp['definition']['string'], 'definition1')
        self.assertEqual(resp['definition']['language'], 'en')

        self.assertEqual(
            resp['uri'], self.NS_ROOT + self.term.get_about_url()[1:]
        )
        self.assertEqual(resp['thesaurus'], self.term.namespace.url)

    def test_two_terms_with_broader_narrower(self):
        term2 = TermFactory(id=2)
        self._initialize(term2, 'prefLabel2', 'definition2', self.english)
        p1 = PropertyTypeFactory(id=1, name='narrower', label='narrower term')
        p2 = PropertyTypeFactory(id=2, name='broader', label='broader term')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url})
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel1')
        self.assertEqual(resp['preferredLabel']['language'], 'en')
        self.assertEqual(resp['definition']['string'], 'definition1')
        self.assertEqual(resp['definition']['language'], 'en')
        self.assertEqual(
            resp['uri'], self.NS_ROOT + self.term.get_about_url()[1:]
        )
        self.assertEqual(resp['thesaurus'], self.term.namespace.url)

    def test_two_terms_without_broader_narrower(self):
        term2 = TermFactory(id=2)
        self._initialize(term2, 'prefLabel2', 'definition2', self.english)
        p1 = PropertyTypeFactory(id=1, name='related', label='related')
        p2 = PropertyTypeFactory(id=2, name='related', label='related')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url})
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]['preferredLabel']['string'], 'prefLabel1')
        self.assertEqual(resp[0]['preferredLabel']['language'], 'en')
        self.assertEqual(resp[0]['definition']['string'], 'definition1')
        self.assertEqual(resp[0]['definition']['language'], 'en')
        self.assertEqual(
            resp[0]['uri'], self.NS_ROOT + self.term.get_about_url()[1:]
        )
        self.assertEqual(resp[0]['thesaurus'], self.term.namespace.url)

        self.assertEqual(resp[1]['preferredLabel']['string'], 'prefLabel2')
        self.assertEqual(resp[1]['preferredLabel']['language'], 'en')
        self.assertEqual(resp[1]['definition']['string'], 'definition2')
        self.assertEqual(resp[1]['definition']['language'], 'en')
        self.assertEqual(
            resp[1]['uri'], self.NS_ROOT + term2.get_about_url()[1:]
        )
        self.assertEqual(resp[1]['thesaurus'], term2.namespace.url)

    def test_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        term2 = TermFactory(id=2)
        self._initialize(term2, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': self.term.namespace.url,
                                  'language': spanish.code})
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel2')
        self.assertEqual(resp['preferredLabel']['language'], 'es')
        self.assertEqual(resp['definition']['string'], 'definition2')
        self.assertEqual(resp['definition']['language'], 'es')
        self.assertEqual(
            resp['uri'], self.NS_ROOT + term2.get_about_url()[1:]
        )
        self.assertEqual(resp['thesaurus'], term2.namespace.url)

    def test_two_namespaces(self):
        theme = ThemeFactory()
        self._initialize(theme, 'prefLabel2', 'definition2', self.english)

        resp = self.app.get(
            self.url + urlencode({'thesaurus_uri': theme.namespace.url})
        )
        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['string'], 'prefLabel2')
        self.assertEqual(resp['preferredLabel']['language'], 'en')
        self.assertEqual(resp['definition']['string'], 'definition2')
        self.assertEqual(resp['definition']['language'], 'en')
        self.assertEqual(
            resp['uri'], self.NS_ROOT + theme.get_about_url()[1:]
        )
        self.assertEqual(resp['thesaurus'], theme.namespace.url)
