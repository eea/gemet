from django.urls import reverse

from .factories import ThemeFactory, PropertyFactory, LanguageFactory
from .factories import VersionFactory, UserFactory
from . import GemetTest
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED


class TestThemesView(GemetTest):
    def setUp(self):
        LanguageFactory()
        VersionFactory()

    def test_no_theme(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')

        self.assertEqual(resp.pyquery('.themes').find("li"), [])

    def test_one_theme(self):
        theme = ThemeFactory()
        PropertyFactory(concept=theme)

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.listing.columns li').length, 1)

        self.assertEqual(resp.pyquery('.listing.columns li a').attr('href'),
                         reverse('theme_concepts',
                                 kwargs={'langcode': 'en',
                                         'theme_code': theme.code})
                         )
        self.assertEqual(resp.pyquery('.listing.columns li a').text(),
                         u'administration')

    def test_contains_more_themes(self):
        theme1 = ThemeFactory(code="1")
        PropertyFactory(concept=theme1, value="Theme 1")
        theme2 = ThemeFactory(code="2")
        PropertyFactory(concept=theme2, value="Theme 2")

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.listing.columns li').length, 2)

        self.assertEqual(
            resp.pyquery('.listing.columns li:eq(0) a').attr('href'),
            reverse('theme_concepts', kwargs={'langcode': 'en',
                                              'theme_code': theme1.code})
        )
        self.assertEqual(resp.pyquery('.listing.columns li:eq(0) a').text(),
                         u'Theme 1'
                         )
        self.assertEqual(
            resp.pyquery('.listing.columns li:eq(1) a').attr('href'),
            reverse('theme_concepts', kwargs={'langcode': 'en',
                                              'theme_code': theme2.code})
        )
        self.assertEqual(resp.pyquery('.listing.columns li:eq(1) a').text(),
                         u'Theme 2'
                         )


class TestThemesViewWithUser(GemetTest):
    def setUp(self):
        self.language = LanguageFactory()
        user = UserFactory()
        VersionFactory()
        self.user = user.username

    def test_pending_name_for_theme(self):
        theme = ThemeFactory(status=PUBLISHED)
        PropertyFactory(concept=theme, value='Old Theme test',
                        language=self.language,
                        status=DELETED_PENDING)
        PropertyFactory(concept=theme, value='New Theme test',
                        language=self.language,
                        status=PENDING)
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.listing.columns li a').text(),
                         'New Theme test')

    def test_new_theme(self):
        theme = ThemeFactory(status=PENDING)
        PropertyFactory(concept=theme, value='New',
                        status=PENDING,
                        language=self.language)
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.listing.columns li a').text(), 'New')
