from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestGetRelatedConcepts(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root') + 'getRelatedConcepts?'
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
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'relation'
            })
        )
        self._response_valid(resp.status_int, resp.content_type)

    def test_invalid_language(self):
        self.assertRaises(
            Fault, self.app.get, self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'relation',
                'language': 'es',
            })
        )

    def test_invalid_concept_uri(self):
        self.assertRaises(
            Fault, self.app.get, self.url + urlencode({
                'concept_uri': 'BAD_CONCEPT_URI',
                'relation_uri': 'relation',
            })
        )

    def test_bad_relation(self):
        term2 = TermFactory(id=2, code='2')
        self._initialize(term2, 'prefLabel2', 'definition2', self.english)
        p1 = PropertyTypeFactory(id=1, name='related', label='related',
                                 uri='in_relation')
        p2 = PropertyTypeFactory(id=2, name='related', label='related',
                                 uri='in_relation')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'BAD_RELATION',
            })
        )
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_two_related_concepts(self):
        term2 = TermFactory(id=2, code='2')
        self._initialize(term2, 'prefLabel2', 'definition2', self.english)
        p1 = PropertyTypeFactory(id=1, name='related', label='related',
                                 uri='in_relation')
        p2 = PropertyTypeFactory(id=2, name='related', label='related',
                                 uri='in_relation')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'in_relation',
            })
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
            resp['uri'],
            self.ENDPOINT_URI + reverse(
                'concept',
                args=(self.english.code, term2.id)
            )
        )
        self.assertEqual(resp['thesaurus'], term2.namespace.url)

    def test_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        term2 = TermFactory(id=2, code='2')
        self._initialize(term2, 'prefLabel2', 'definition2', spanish)
        p1 = PropertyTypeFactory(id=1, name='related', label='related',
                                 uri='in_relation')
        p2 = PropertyTypeFactory(id=2, name='related', label='related',
                                 uri='in_relation')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'relation_uri': 'in_relation',
            })
        )
        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 0)