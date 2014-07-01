from urllib import urlencode

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestHasConcept(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.url = reverse('api_root', args=['hasConcept']) + '?'
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
        resp = self.app.get(
            self.url + urlencode({'concept_uri': 'BAD_THESAURUS_URI'})
        )
        self.assertEqual(False, resp.json)

    def test_has_true(self):
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + self.term.code
        }))

        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(True, resp.json)

    def test_has_false(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        self._initialize(self.term, 'prefLabel2', 'definition2', spanish)
        resp = self.app.get(self.url + urlencode({
            'concept_uri': self.NS_ROOT + 'concept/' + '9999'
        }))

        self._response_valid(resp.status_int, resp.content_type)
        self.assertEqual(False, resp.json)
