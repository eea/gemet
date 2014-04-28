import pyquery

from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestThemeConceptsView(WebTest):
    def setUp(self):
        self.ns_concept = NamespaceFactory(id=2, heading="Concepts")
        self.theme = ConceptFactory()

        PropertyFactory(concept=self.theme)
        self.pt1 = PropertyTypeFactory(id=1, name="themeMember",
                                       label="Theme member")
        self.pt2 = PropertyTypeFactory(id=2, name="theme", label="Theme")

    def test_one_theme_concept(self):
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

        """
        after TO_DO list

        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept value')

    def test_more_theme_concepts(self):
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

        #after TO_DO list. An a href needed
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept 1')

        #after TO_DO list. An a href needed
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(1) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """

        self.assertEqual(resp.pyquery('.concepts li:eq(1)').text(),
                         u'Concept 2')

    def test_letter_selected(self):
        concept2 = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept2, value="A_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        concept3 = ConceptFactory(id=3, code="3", namespace=self.ns_concept)
        PropertyFactory(concept=concept3, value="B_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept3)
        RelationFactory(property_type=self.pt2, source=concept3,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})

        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))
        self.assertEqual(200, resp.status_int)
        for concept_index in range(0, len(resp.pyquery('.concepts li'))):
            self.assertEqual(resp.pyquery('.concepts li:eq({0})'
                                          .format(concept_index)).text()[0],
                             'A')

        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=2))
        self.assertEqual(200, resp.status_int)
        for concept_index in range(0, len(resp.pyquery('.concepts li'))):
            self.assertEqual(resp.pyquery('.concepts li:eq({0})'
                                          .format(concept_index)).text()[0],
                             'B')