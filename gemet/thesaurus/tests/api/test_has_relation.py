from urllib.parse import urlencode
from xmlrpc.client import Fault

from django.urls import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
    PropertyTypeFactory,
    RelationFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestHasRelation(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['hasRelation']) + '?'
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
        resp = self.app.get(self.url + urlencode({
            'concept_uri': 'BAD_THESAURUS_URI',
            'relation_uri': 'relation_uri',
            'object_uri': self.NS_ROOT + 'concept/' + self.term.code,
        }))
        self._response_valid(resp.status_code, resp.content_type)
        self.assertEqual(False, resp.json)

    def test_missing_concept_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'relation_uri': 'relation_uri',
            'object_uri': self.NS_ROOT + 'concept/' + self.term.code,
        }))

    def test_invalid_object_uri(self):
        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'relation_uri',
                'object_uri': 'BAD_THESAURUS_URI'
            }))
        self._response_valid(resp.status_code, resp.content_type)
        self.assertEqual(False, resp.json)

    def test_missing_object_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            'relation_uri': 'relation_uri',
        }))

    def test_missing_relation_uri(self):
        self.assertRaises(Fault, self.app.get, self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            'object_uri': self.NS_ROOT + 'concept/' + self.term.code,
        }))

    def _initialize_relations(self):
        self.term2 = TermFactory(id=2, code='2')
        self._initialize(self.term2, 'prefLabel2', 'definition2', self.english)
        p = PropertyTypeFactory(uri='relation#related')
        RelationFactory(source=self.term, target=self.term2, property_type=p)

    def test_no_relation(self):
        self._initialize_relations()

        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            'relation_uri': 'related',
            'object_uri': self.NS_ROOT + 'concept/' + self.term2.code
        }))

        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(False, resp.json)

    def test_true(self):
        self._initialize_relations()

        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            'relation_uri': 'relation#related',
            'object_uri': self.NS_ROOT + 'concept/' + self.term2.code
        }))

        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(True, resp.json)

    def test_false(self):
        self._initialize_relations()

        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term2.code,
            'relation_uri': 'relation#related',
            'object_uri': self.NS_ROOT + 'concept/' + self.term.code,
        }))

        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(False, resp.json)
