from django.core.urlresolvers import reverse

from .factories import LanguageFactory, InspireThemeFactory, PropertyFactory
from . import GemetTest


class TestInspireThemesView(GemetTest):
    def setUp(self):
        LanguageFactory()

    def test_no_theme(self):
        url = reverse('inspire-themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 0)

    def test_one_theme(self):
        theme = InspireThemeFactory()
        PropertyFactory(concept=theme, value='Addresses')

        url = reverse('inspire-themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0) a')
                         .attr('href'),
                         reverse('inspire-theme',
                                 kwargs={'langcode': 'en',
                                         'concept_id': theme.id})
                         )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0) a').text(),
                         u'Addresses')
