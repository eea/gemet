from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    LanguageFactory,
    NamespaceFactory,
)


class TestThemesView(WebTest):

    def setUp(self):
        LanguageFactory()
        NamespaceFactory()

    def test_one_theme(self):
        ConceptFactory()
        PropertyFactory()

        url = reverse('themes', args=['en'])
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
