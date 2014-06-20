from django.core.urlresolvers import reverse

from .factories import (
    ThemeFactory,
    PropertyFactory,
    LanguageFactory,
)
from . import GemetTest


class TestThemesView(GemetTest):
    def setUp(self):
        LanguageFactory()

    def test_no_theme(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('.themes').find("li"), [])

    def test_one_theme(self):
        theme = ThemeFactory()
        PropertyFactory(concept=theme)

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.listing.columns li').length, 1)

        self.assertEqual(resp.pyquery('.listing.columns li a').attr('href'),
                         reverse('theme_concepts',
                                 kwargs={'langcode': 'en',
                                         'theme_id': theme.id})
                         )
        self.assertEqual(resp.pyquery('.listing.columns li a').text(),
                         u'administration')

    def test_contains_more_themes(self):
        theme1 = ThemeFactory(id=1, code="1")
        PropertyFactory(concept=theme1, value="Theme 1")
        theme2 = ThemeFactory(id=2, code="2")
        PropertyFactory(concept=theme2, value="Theme 2")

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.listing.columns li').length, 2)

        self.assertEqual(resp.pyquery('.listing.columns li:eq(0) a').attr('href'),
                         reverse('theme_concepts',
                                 kwargs={'langcode': 'en',
                                         'theme_id': theme1.id})
                         )
        self.assertEqual(resp.pyquery('.listing.columns li:eq(0) a').text(),
                         u'Theme 1'
                         )
        self.assertEqual(resp.pyquery('.listing.columns li:eq(1) a').attr('href'),
                         reverse('theme_concepts',
                                 kwargs={'langcode': 'en',
                                         'theme_id': theme2.id})
                         )
        self.assertEqual(resp.pyquery('.listing.columns li:eq(1) a').text(),
                         u'Theme 2'
                         )
