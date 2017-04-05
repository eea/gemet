from django.core.urlresolvers import reverse
from django.conf import settings

from .factories import PropertyFactory, PropertyTypeFactory, RelationFactory
from .factories import TermFactory, ThemeFactory
from . import GemetTest, ERROR_404


class TestThemeView(GemetTest):
    def setUp(self):
        self.theme = ThemeFactory()
        PropertyFactory(concept=self.theme, name="prefLabel",
                        value="some prefLabel")

    def test_theme_no_concept(self):
        url = reverse('theme', kwargs={'code': self.theme.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content ul:eq(0)').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         "English some prefLabel")

    def test_theme_one_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, name="prefLabel",
                        value="concept prefLabel")
        pt1 = PropertyTypeFactory(name="themeMember",
                                  label="Theme member")
        pt2 = PropertyTypeFactory(name="theme", label="Theme")
        RelationFactory(property_type=pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=pt2, source=concept,
                        target=self.theme)
        url = reverse('theme', kwargs={'code': self.theme.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content .listing li').size(), 1)
        self.assertEqual(resp.pyquery('.content .listing li').text(),
                         "concept prefLabel")
        self.assertEqual(resp.pyquery('.content li.clearfix').size(), 1)
        self.assertEqual(resp.pyquery('.content li.clearfix').text(),
                         "English some prefLabel")

    def test_theme_two_concepts(self):
        concept1 = TermFactory()
        PropertyFactory(concept=concept1, name="prefLabel",
                        value="concept1 prefLabel")
        pt1 = PropertyTypeFactory(name="themeMember",
                                  label="Theme member")
        pt2 = PropertyTypeFactory(name="theme", label="Theme")
        RelationFactory(property_type=pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=pt2, source=concept1,
                        target=self.theme)
        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, name="prefLabel",
                        value="concept2 prefLabel")
        pt3 = PropertyTypeFactory(name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(name="theme", label="Theme")
        RelationFactory(property_type=pt3, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=pt4, source=concept2,
                        target=self.theme)
        url = reverse('theme', kwargs={'code': self.theme.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content .listing li').size(), 2)
        self.assertEqual(resp.pyquery('.content .listing li:eq(0)').text(),
                         "concept1 prefLabel")
        self.assertEqual(resp.pyquery('.content .listing li:eq(1)').text(),
                         "concept2 prefLabel")
        self.assertEqual(resp.pyquery('.content li.clearfix').size(), 1)
        self.assertEqual(resp.pyquery('.content li.clearfix').text(),
                         "English some prefLabel")

    def test_redirect(self):
        url = reverse('theme', kwargs={'code': self.theme.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content h5.h5-url').text().split()[-1]
        self.assertTrue(settings.GEMET_URL in url)
        self.assertTrue(url.endswith(self.theme.code))

    def test_404_error(self):
        url = reverse('theme', kwargs={'code': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
