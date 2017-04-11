from django.core.urlresolvers import reverse

from .factories import (
    LanguageFactory,
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    ThemeFactory,
    TermFactory,
    UserFactory
)
from . import GemetTest, ERROR_404
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED


class TestThemeConceptsView(GemetTest):
    def setUp(self):
        self.theme = ThemeFactory()

        PropertyFactory(concept=self.theme, name="propertyName")
        self.pt1 = PropertyTypeFactory(name="themeMember",
                                       label="Theme member")
        self.pt2 = PropertyTypeFactory(name="theme", label="Theme")

    def test_one_theme_one_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': self.theme.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0)').length, 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li a').attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept.code})
                         )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'Concept value')

    def test_one_theme_two_concepts(self):
        PropertyFactory(concept=self.theme, name="prefLabel")
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value="Concept 1")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=self.pt2, source=concept1,
                        target=self.theme)

        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value="Concept 2")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': self.theme.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept1.code})
        )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'Concept 1')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(1) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept2.code})
        )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(1)').text(),
                         'Concept 2')

    def test_letter_selected_filter_one_language(self):
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value="A_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=self.pt2, source=concept1,
                        target=self.theme)

        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value="B_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        url = "{url}?letter={letter}"\
              .format(url=reverse('theme_concepts',
                                  kwargs={'langcode': 'en',
                                          'theme_code': self.theme.code}),
                      letter=1)
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'A_CONCEPT')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept1.code})
        )

    def test_letter_selected_filter_two_concepts_two_languages(self):
        english_concept = TermFactory(code="1")
        PropertyFactory(concept=english_concept, value="A_EN_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=english_concept)
        RelationFactory(property_type=self.pt2, source=english_concept,
                        target=self.theme)

        spanish = LanguageFactory(code='es', name='Spanish')
        spanish_theme = ThemeFactory(code="5")
        PropertyFactory(concept=spanish_theme)
        spanish_concept = TermFactory(code="2")
        PropertyFactory(concept=spanish_concept, language=spanish,
                        name="prefLabel", value="A_ES_CONCEPT")
        RelationFactory(property_type=self.pt1, source=spanish_theme,
                        target=spanish_concept)
        RelationFactory(property_type=self.pt2, source=spanish_concept,
                        target=spanish_theme)

        url = "{url}?letter={letter}"\
              .format(url=reverse('theme_concepts',
                                  kwargs={'langcode': 'en',
                                          'theme_code': self.theme.code}),
                      letter=1)
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'A_EN_CONCEPT')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': english_concept.code})
        )

    def test_letter_selected_filter_one_concept_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        concept = TermFactory()
        PropertyFactory(concept=concept, value="A_EN_CONCEPT")
        PropertyFactory(concept=concept, language=spanish, name="prefLabel",
                        value="A_ES_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = "{url}?letter={letter}"\
              .format(url=reverse('theme_concepts',
                                  kwargs={'langcode': 'en',
                                          'theme_code': self.theme.code}),
                      letter=1)
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'A_EN_CONCEPT')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept.code})
        )

    def test_404_error_letter_out_of_range(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = "{url}?letter={letter}"\
              .format(url=reverse('theme_concepts',
                                  kwargs={'langcode': 'en',
                                          'theme_code': self.theme.code}),
                      letter=100)
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_error_concept_id(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': concept.code})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())


class TestThemeConceptsViewWithUser(GemetTest):
    def setUp(self):
        self.theme = ThemeFactory()
        self.theme_name = PropertyFactory(concept=self.theme,
                                          value="Theme",
                                          status=PUBLISHED)
        user = UserFactory()
        self.user = user.username
        self.pt1 = PropertyTypeFactory(name="themeMember",
                                       label="Theme member")
        self.pt2 = PropertyTypeFactory(name="theme", label="Theme")

    def test_pending_name_for_theme(self):
        self.theme_name.status = DELETED_PENDING
        PropertyFactory(concept=self.theme, value="New Theme",
                        status=PENDING)
        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': self.theme.code})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('h1 i').text(), 'New Theme')

    def test_pending_relation_with_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept value",
                        status=PUBLISHED)
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept, status=PENDING)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme, status=PENDING)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': self.theme.code})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content ul:eq(0)').length, 1)
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept.code})
        )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'Concept value')

    def test_pending_name_for_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Old Concept value",
                        status=DELETED_PENDING)
        PropertyFactory(concept=concept, value="New Concept value",
                        status=PENDING)
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept, status=PENDING)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme, status=PENDING)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_code': self.theme.code})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'New Concept value')
