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
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 0)
        self.assertEqual(resp.pyquery('.well a').length, 0)
        self.assertEqual(resp.pyquery('.well span').length, 0)

    def test_one_theme(self):
        theme = InspireThemeFactory()
        PropertyFactory(concept=theme, value='Addresses')

        url = reverse('inspire-themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 1)
        self.assertEqual(resp.pyquery('.themes li a').attr('href'),
                         reverse('inspire-theme',
                                 kwargs={'langcode': 'en',
                                         'concept_id': theme.id})
                         )
        self.assertEqual(resp.pyquery('.themes li a').text(), u'Addresses')
        self.assertEqual(resp.pyquery('.well a').length, 0)
        self.assertEqual(resp.pyquery('.well span').text(), 'en')
