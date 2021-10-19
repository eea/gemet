from urllib.parse import urlencode
from xmlrpc.client import Fault
import unittest

from django.urls import reverse
from django.db import connection

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
    ThemeFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestGetConceptsMatchingKeyword(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root',
                           args=['getConceptsMatchingKeyword']) + '?'
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

    def test_missing_search_mode(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
            'keyword': 'prefLabel1',
        }))

    def test_invalid_search_mode(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'search_mode': 5,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
            'keyword': 'prefLabel1',
        }))

    def test_default_language(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 0,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'keyword': 'prefLabel1',
        }))
        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json.pop()
        self.assertEqual(resp['preferredLabel']['language'], DEFAULT_LANGCODE)

    def test_invalid_language(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'search_mode': 0,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': 'es',
            'keyword': 'prefLabel1',
        }))

    def test_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(self.term, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'search_mode': 1,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'keyword': 'prefLabel',
            'language': self.english.code,
        }))
        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['preferredLabel']['language'], self.english.code)

    def test_missing_keyword(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'search_mode': 0,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
            'language': self.english.code,
        }))

    def test_invalid_thesaurus_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'search_mode': 0,
            'thesaurus_uri': 'BAD_THESAURUS_URI',
            'language': self.english.code,
            'keyword': 'prefLabel1',
        }))

    def test_specific_thesaurus_uri(self):
        theme = ThemeFactory()
        self._initialize(theme, 'prefLabel2', 'definition2', self.english)
        resp = self.app.get(self.url + urlencode({
            'search_mode': 1,
            'keyword': 'prefLabel',
            'language': self.english.code,
            'thesaurus_uri': self.NS_ROOT + 'concept/',
        }))
        self._response_valid(resp.status_code, resp.content_type)
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

    def test_missing_thesaurus_uri(self):
        theme = ThemeFactory()
        self._initialize(theme, 'prefLabel2', 'definition2', self.english)
        resp = self.app.get(self.url + urlencode({
            'search_mode': 1,
            'keyword': 'prefLabel',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
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
            resp[1]['uri'], self.NS_ROOT + theme.get_about_url()[1:]
        )
        self.assertEqual(resp[1]['thesaurus'], theme.namespace.url)

    def test_0_search_with_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 0,
            'keyword': 'prefLabel1',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_0_search_no_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 0,
            'keyword': 'prefLabel',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_1_search_with_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 1,
            'keyword': 'pref',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_1_search_no_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 1,
            'keyword': 'Label',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_2_search_with_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 2,
            'keyword': 'Label1',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_2_search_no_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 2,
            'keyword': 'Label',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_3_search_with_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 3,
            'keyword': 'Label',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_3_search_no_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 3,
            'keyword': 'xyz',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_4_search_0(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 0,
            'keyword': 'prefLabel1',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_4_search_1(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 4,
            'keyword': 'pref',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_4_search_2(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 4,
            'keyword': 'Label1',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_4_search_3(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 4,
            'keyword': 'Label',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)

    def test_4_search_no_result(self):
        resp = self.app.get(self.url + urlencode({
            'search_mode': 4,
            'keyword': 'xyz',
            'language': self.english.code,
        }))

        self._response_valid(resp.status_code, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)
