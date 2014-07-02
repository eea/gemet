from urllib import urlencode
from xmlrpclib import Fault

from django.core.urlresolvers import reverse

from gemet.thesaurus.tests.factories import (
    TermFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestOthers(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = 'http://www.eionet.europa.eu'
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
            'callback(' + self.app.get(url).body + ')',
        )
