from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
    ThemeFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestGetConceptsMatchingRegexByThesaurus(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root') + 'getConceptsMatchingRegexByThesaurus?'
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

    def test_default_language(self):
        resp = self.app.get(self.url + urlencode({
            'regex': '^pref',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))
        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json.pop()
        self.assertEqual(resp['preferredLabel']['language'], DEFAULT_LANGCODE)

    def test_invalid_language(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'regex': '^pref',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': 'es',
        }))

    def test_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(self.term, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'regex': '^pref',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
        }))
        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['language'], self.english.code)

    def test_missing_regex(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
        }))

    def test_invalid_thesaurus_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'regex': '^pref',
            'thesaurus_uri': 'BAD_THESAURUS_URI',
            'language': self.english.code,
        }))

    def test_missing_thesaurus_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'regex': '^pref',
            'language': self.english.code,
        }))

    def test_specific_thesaurus_uri(self):
        theme = ThemeFactory()
        self._initialize(theme, 'prefLabel2', 'definition2', self.english)
        resp = self.app.get(self.url + urlencode({
            'regex': '^pref',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def _initialize_some_terms(self):
        term2 = TermFactory(id=2, code='2')
        term3 = TermFactory(id=3, code='3')
        term4 = TermFactory(id=4, code='4')
        term5 = TermFactory(id=5, code='5')
        self._initialize(term2, 'refLabel', '', self.english)
        self._initialize(term3, 'prefLabel', '', self.english)
        self._initialize(term4, 'refLabel1', '', self.english)
        self._initialize(term5, 'prefxyzLabel1', '', self.english)

    def test_begins_with(self):
        self._initialize_some_terms()
        resp = self.app.get(self.url + urlencode({
            'regex': '^pre',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 3)

    def test_ends_with(self):
        self._initialize_some_terms()
        resp = self.app.get(self.url + urlencode({
            'regex': 'Label$',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 2)

    def test_all_operators(self):
        self._initialize_some_terms()
        resp = self.app.get(self.url + urlencode({
            'regex': '^pre.+abe.+$',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 3)

    def test_no_operator(self):
        self._initialize_some_terms()
        resp = self.app.get(self.url + urlencode({
            'regex': 'refLabel',
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 4)
