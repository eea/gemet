from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    ThemeFactory,
)
from . import GemetTest, ERROR_404


class TestThemeView(GemetTest):
    def setUp(self):
        self.theme = ThemeFactory()
        PropertyFactory(concept=self.theme, name="prefLabel",
                        value="some prefLabel")

    def test_theme_no_concept(self):
        url = reverse('theme', kwargs={'concept_id': self.theme.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p:eq(2)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p:eq(3)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('ul:eq(1)').size(), 1)
        self.assertEqual(resp.pyquery('ul:eq(1) li').text(),
                         "English some prefLabel")

    def test_theme_one_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, name="prefLabel",
                        value="concept prefLabel")
        pt1 = PropertyTypeFactory(id=1, name="themeMember",
                                  label="Theme member")
        pt2 = PropertyTypeFactory(id=2, name="theme", label="Theme")
        RelationFactory(property_type=pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=pt2, source=concept,
                        target=self.theme)
        url = reverse('theme', kwargs={'concept_id': self.theme.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p:eq(2)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p:eq(3)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('ul:eq(2) li').size(), 1)
        self.assertEqual(resp.pyquery('ul:eq(2) li').text(),
                         "concept prefLabel")
        self.assertEqual(resp.pyquery('ul:eq(1) li').size(), 1)
        self.assertEqual(resp.pyquery('ul:eq(1) li').text(),
                         "English some prefLabel")

    def test_theme_two_concepts(self):
        concept1 = TermFactory()
        PropertyFactory(concept=concept1, name="prefLabel",
                        value="concept1 prefLabel")
        pt1 = PropertyTypeFactory(id=1, name="themeMember",
                                  label="Theme member")
        pt2 = PropertyTypeFactory(id=2, name="theme", label="Theme")
        RelationFactory(property_type=pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=pt2, source=concept1,
                        target=self.theme)
        concept2 = TermFactory(id=2, code="2")
        PropertyFactory(concept=concept2, name="prefLabel",
                        value="concept2 prefLabel")
        pt3 = PropertyTypeFactory(id=3, name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(id=4, name="theme", label="Theme")
        RelationFactory(property_type=pt3, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=pt4, source=concept2,
                        target=self.theme)
        url = reverse('theme', kwargs={'concept_id': self.theme.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p:eq(2)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p:eq(3)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('ul:eq(2) li').size(), 2)
        self.assertEqual(resp.pyquery('ul:eq(2) li:eq(0)').text(),
                         "concept1 prefLabel")
        self.assertEqual(resp.pyquery('ul:eq(2) li:eq(1)').text(),
                         "concept2 prefLabel")
        self.assertEqual(resp.pyquery('ul:eq(1)').size(), 1)
        self.assertEqual(resp.pyquery('ul:eq(1)').text(),
                         "English some prefLabel")

    def test_redirect(self):
        url = reverse('theme', kwargs={'concept_id': self.theme.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('p:eq(4)').text()
        self.assertEqual(302, self.app.get(url).status_int)

    def test_404_error(self):
        url = reverse('theme', kwargs={'concept_id': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404').text())
