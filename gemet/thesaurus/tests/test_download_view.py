from django.core.urlresolvers import reverse
from . import GemetTest, ERROR_404

from .factories import (
    LanguageFactory,
)

class TestDownloadView(GemetTest):
    def setUp(self):
        LanguageFactory()
        self.url = reverse('download', kwargs={'langcode': 'en'})

    def test_links(self):
        resp = self.app.get(self.url)

        self.assertEqual(200, resp.status_int)
        for link in resp.pyquery('.content .listing a'):
            tmp = self.app.get(resp.pyquery(link).attr('href'))
            self.assertEqual(200, tmp.status_int)

    def test_page_access(self):
        resp = self.app.get(self.url)
        self.assertEqual(200, resp.status_int)

    def test_form_definitions(self):
        resp = self.app.get(self.url)
        resp = resp.forms['definitions-form'].submit('type')

        self.assertEqual(302, resp.status_int)
        resp = resp.follow()
        self.assertEqual(200, resp.status_int)

    def test_form_groups(self):
        resp = self.app.get(self.url)
        resp = resp.forms['groups-form'].submit('type')

        self.assertEqual(302, resp.status_int)
        resp = resp.follow()
        self.assertEqual(200, resp.status_int)

    def test_form_unknown(self):
        resp = self.app.get(self.url)
        resp.forms['groups-form'].get('type').force_value('unknown')
        resp = resp.forms['groups-form'].submit('type')

        self.assertEqual(200, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

