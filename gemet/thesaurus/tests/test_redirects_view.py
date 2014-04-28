import pyquery

from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django.test.utils import ContextList

from .factories import (
    ConceptFactory,
    PropertyFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestRedirectsView(WebTest):
    def test_index_html(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get('/index_html')

        self.assertEqual(302, resp.status_int)
        self.assertRedirects(resp, url)

    def test_groups(self):
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get('/groups')

        self.assertEqual(302, resp.status_int)
        self.assertRedirects(resp, url)
