from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    LanguageFactory,
    ThemeFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestAllConceptRelatives(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['getAllConceptRelatives']) + '?'
        self.term = TermFactory()

    def _response_valid(self, status, content_type):
        self.assertEqual(200, status)
        self.assertEqual(content_type, 'application/json')

    def test_invalid_concept_uri(self):
        self.assertRaises(
            Fault, self.app.get, self.url + urlencode({
                'concept_uri': 'INVALID_CONCEPT_URI',
            })
        )

    def test_missing_concept_uri(self):
        self.assertRaises(Fault, self.app.get, self.url)

    def test_bad_relation(self):
        term2 = TermFactory(id=2, code='2')
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

    def test_bad_thesaurus_uri(self):
        term2 = TermFactory(id=2, code='2')
        p1 = PropertyTypeFactory(id=1, name='related', label='related',
                                 uri='in_relation')
        p2 = PropertyTypeFactory(id=2, name='related', label='related',
                                 uri='in_relation')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'target_thesaurus_uri': 'BAD_THESAURUS_URI',
            })
        )
        resp = resp.json
        self.assertEqual(len(resp), 0)

    def test_all_3_parameters(self):
        term2 = TermFactory(id=2, code='2')
        p1 = PropertyTypeFactory(id=1, name='broader', label='broader term',
                                 uri='broader_uri')
        p2 = PropertyTypeFactory(id=2, name='narrower', label='narrower term',
                                 uri='narrower_uri')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        theme = ThemeFactory()
        p3 = PropertyTypeFactory(id=3, name='broader', label='broader term',
                                 uri='broader_uri')
        p4 = PropertyTypeFactory(id=4, name='narrower', label='narrower term',
                                 uri='narrower_uri')
        RelationFactory(property_type=p3, source=self.term, target=theme)
        RelationFactory(property_type=p4, source=theme, target=self.term)

        theme2 = ThemeFactory(id=5, code='5')
        p5 = PropertyTypeFactory(id=5, name='related', label='related',
                                 uri='related_uri')
        p6 = PropertyTypeFactory(id=6, name='related', label='related',
                                 uri='related_uri')
        RelationFactory(property_type=p5, source=self.term, target=theme2)
        RelationFactory(property_type=p6, source=theme2, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
                'target_thesaurus_uri': self.NS_ROOT + 'theme/',
                'relation_uri': p3.uri,
            })
        )
        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        resp = resp.pop()
        self.assertEqual(resp['source'],
                         self.NS_ROOT + 'concept/' + self.term.code)
        self.assertEqual(resp['relation'], p3.uri)
        self.assertEqual(
            resp['target'],
            self.ENDPOINT_URI + reverse(
                'theme', args=(self.english.code, theme.id)
            )
        )

    def test_optional_parameters(self):
        term2 = TermFactory(id=2, code='2')
        spanish = LanguageFactory(code='es', name='Spanish')
        PropertyFactory(concept=term2, language=spanish)
        p1 = PropertyTypeFactory(id=1, name='broader', label='broader term',
                                 uri='broader_uri')
        p2 = PropertyTypeFactory(id=2, name='narrower', label='narrower term',
                                 uri='narrower_uri')
        RelationFactory(property_type=p1, source=self.term, target=term2)
        RelationFactory(property_type=p2, source=term2, target=self.term)

        theme = ThemeFactory()
        p3 = PropertyTypeFactory(id=3, name='theme', label='Theme',
                                 uri='theme_uri')
        p4 = PropertyTypeFactory(id=4, name='themeMember', label='Theme member',
                                 uri='theme_member_uri')
        RelationFactory(property_type=p3, source=self.term, target=theme)
        RelationFactory(property_type=p4, source=theme, target=self.term)

        resp = self.app.get(
            self.url + urlencode({
                'concept_uri': self.NS_ROOT + 'concept/' + self.term.code,
            })
        )
        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]['source'],
                         self.NS_ROOT + 'concept/' + self.term.code)
        self.assertEqual(resp[0]['relation'], p1.uri)
        self.assertEqual(
            resp[0]['target'],
            self.ENDPOINT_URI + reverse(
                'concept', args=(DEFAULT_LANGCODE, term2.id)
            )
        )
        self.assertEqual(resp[1]['source'],
                         self.NS_ROOT + 'concept/' + self.term.code)
        self.assertEqual(resp[1]['relation'], p3.uri)
        self.assertEqual(
            resp[1]['target'],
            self.ENDPOINT_URI + reverse(
                'theme', args=(DEFAULT_LANGCODE, theme.id)
            )
        )
