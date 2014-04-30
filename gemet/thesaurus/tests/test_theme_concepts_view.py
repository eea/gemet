import pyquery

from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    LanguageFactory,
    PropertyFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestThemeConceptsView(WebTest):
    def setUp(self):
        self.theme = ConceptFactory()
        self.ns_concept = NamespaceFactory(id=2, heading="Concepts")

        PropertyFactory(concept=self.theme)
        self.pt1 = PropertyTypeFactory(id=1, name="themeMember",
                                       label="Theme member")
        self.pt2 = PropertyTypeFactory(id=2, name="theme", label="Theme")

    def test_one_theme_one_concept(self):
        concept = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.concepts li').length, 1)
        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept value')

    def test_one_theme_two_concepts(self):
        concept1 = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept1, value="Concept 1")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=self.pt2, source=concept1,
                        target=self.theme)

        concept2 = ConceptFactory(id=3, code="3", namespace=self.ns_concept)
        PropertyFactory(concept=concept2, value="Concept 2")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('concept',
                                             kwargs={'langcode': 'en',
                                                     'concept_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept 1')
        self.assertEqual(resp.pyquery('.concepts li:eq(1) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('concept',
                                             kwargs={'langcode': 'en',
                                                     'concept_id': 3}))
                         )
        self.assertEqual(resp.pyquery('.concepts li:eq(1)').text(),
                         u'Concept 2')

    def test_letter_selected_filter_one_language(self):
        concept1 = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept1, value="A_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=self.pt2, source=concept1,
                        target=self.theme)

        concept2 = ConceptFactory(id=3, code="3", namespace=self.ns_concept)
        PropertyFactory(concept=concept2, value="B_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})

        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.concepts').children().size(), 1)
        self.assertEqual(resp.pyquery('.concepts li a').text()[0], 'A')
        self.assertEqual(resp.pyquery('.concepts li a').attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )

    def test_letter_selected_filter_two_concepts_two_languages(self):
        english_concept = ConceptFactory(id=2, code="2",
                                         namespace=self.ns_concept)
        PropertyFactory(concept=english_concept, value="A_EN_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=english_concept)
        RelationFactory(property_type=self.pt2, source=english_concept,
                        target=self.theme)

        spanish = LanguageFactory(code='es', name='Spanish')
        spanish_theme = ConceptFactory(id=3, code="3")
        PropertyFactory(concept=spanish_theme)
        spanish_concept = ConceptFactory(id=4, code="4",
                                         namespace=self.ns_concept)
        PropertyFactory(concept=spanish_concept, language=spanish,
                        name="prefLabel", value="A_ES_CONCEPT")
        RelationFactory(property_type=self.pt1, source=spanish_theme,
                        target=spanish_concept)
        RelationFactory(property_type=self.pt2, source=spanish_concept,
                        target=spanish_theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.concepts').children().size(), 1)
        self.assertEqual(resp.pyquery('.concepts li a').text()[0], 'A')
        self.assertEqual(resp.pyquery('.concepts li a').attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )

    def test_letter_selected_filter_one_concept_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')
        concept = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept, value="A_EN_CONCEPT")
        PropertyFactory(concept=concept, language=spanish, name="prefLabel",
                        value="A_ES_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.concepts').children().size(), 1)
        self.assertEqual(resp.pyquery('.concepts li a').text()[0], 'A')
        self.assertEqual(resp.pyquery('.concepts li a').attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )

    def test_404_error_letter_out_of_range(self):
        concept = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = "{url}?letter={letter}"\
              .format(url=reverse('theme_concepts', kwargs={'langcode': 'en',
                                                            'theme_id': 1}),
                      letter=100)
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)

    def test_404_error_concept_id(self):
        concept = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts', kwargs={'langcode': 'en',
                                                'theme_id': 2})
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)