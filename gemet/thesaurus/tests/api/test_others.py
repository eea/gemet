from urllib.parse import urlencode
from xmlrpc.client import Fault

from django.urls import reverse

from gemet.thesaurus.tests.factories import (
    TermFactory,
    PropertyFactory,
    InspireThemeFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest
from gemet.thesaurus import DEFAULT_LANGCODE


class TestOthers(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.NS_ROOT = 'http://www.eionet.europa.eu/gemet/'
        self.term = TermFactory()

    def test_invalid_method_name(self):
        url = reverse('api_root', args=['invalidMethodName'])
        self.assertRaises(Fault, self.app.get, url)

    def test_url_with_empty_jsonp(self):
        url_jsonp = (
            reverse('api_root', args=['getAvailableThesauri']) + '?' +
            urlencode({'language': self.english.code, 'jsonp': ''})
        )
        url = (
            reverse('api_root', args=['getAvailableThesauri']) + '?' +
            urlencode({'language': self.english.code})
        )
        self.assertEqual(self.app.get(url_jsonp).body, self.app.get(url).body)

    def test_url_with_nonempty_jsonp(self):
        url_jsonp = (
            reverse('api_root', args=['getAvailableThesauri']) + '?' +
            urlencode({'language': self.english.code, 'jsonp': 'callback'})
        )
        url = (
            reverse('api_root', args=['getAvailableThesauri']) + '?' +
            urlencode({'language': self.english.code})
        )

        self.assertEqual(
            self.app.get(url_jsonp).body,
            bytes('callback(',  encoding='utf8') + self.app.get(url).body + bytes(')',  encoding='utf8'),
        )

    def test_inspire_theme_case(self):
        url = reverse('api_root', args=['getConcept']) + '?'
        inspire = InspireThemeFactory()
        resp = self.app.get(url + urlencode({
            'concept_uri': 'http://inspire.ec.europa.eu/theme/' + inspire.code,
        }))

        self.assertEqual(200, resp.status_code)

    def test_home_redirect(self):
        url = reverse('api_root', args=[''])
        resp = self.app.get(url)

        self.assertEqual(resp.status_code, 301)
        resp = resp.follow()
        self.assertEqual(resp.status_code, 200)
        redirect_url = resp.request.url
        home_url = reverse('themes', args=[DEFAULT_LANGCODE])
        self.assertTrue(redirect_url.endswith(home_url))

    def test_topmost_concepts_null_pref_label(self):
        PropertyFactory(concept=self.term, name='definition',
                        value='definition', language=self.english)
        url = reverse('api_root', args=['getTopmostConcepts']) + '?'
        resp = self.app.get(
            url + urlencode({'thesaurus_uri': self.term.namespace.url})
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        resp = resp.json
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]['definition']['string'], 'definition')
        self.assertEqual(resp[0]['definition']['language'], self.english.code)
        self.assertEqual(
            resp[0]['uri'], self.NS_ROOT + self.term.get_about_url()[1:]
        )
        self.assertEqual(resp[0]['thesaurus'], self.term.namespace.url)
        self.assertFalse(['preferredLabel'] in list(resp[0].keys()))
