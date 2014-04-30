from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    LanguageFactory,
)


class TestThemesView(WebTest):
    def setUp(self):
        LanguageFactory()

    def test_no_theme(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('.themes').children(), [])

    def test_one_theme(self):
        theme = ConceptFactory()
        PropertyFactory(concept=theme)

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 1)

        self.assertEqual(resp.pyquery('.themes li a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        self.assertEqual(resp.pyquery('.themes li a').text(),
                         u'administration')

    def test_contains_more_themes(self):
        theme1 = ConceptFactory(id=1, code="1")
        PropertyFactory(concept=theme1, value="Theme 1")
        theme2 = ConceptFactory(id=2, code="2")
        PropertyFactory(concept=theme2, value="Theme 2")

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 2)

        self.assertEqual(resp.pyquery('.themes li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(0) a').text(),
                         u'Theme 1'
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').text(),
                         u'Theme 2'
                         )
