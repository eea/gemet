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


class TestAlphabeticView(WebTest):
    def test_no_concepts(self):
        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children(), [])

    def test_one_concept(self):
        ns = NamespaceFactory(heading="Concepts")
        concept = ConceptFactory(namespace=ns)
        PropertyFactory(concept=concept)

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children().size(), 1)
        self.assertEqual(resp.pyquery(".concepts li a").text(),
                         'administration')
        self.assertEqual(resp.pyquery(".concepts li a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 1}))
                         )

    def test_more_concepts(self):
        ns = NamespaceFactory(heading="Concepts")
        concept1 = ConceptFactory(id=1, code="1", namespace=ns)
        PropertyFactory(concept=concept1, value="Concept1")
        concept2 = ConceptFactory(id=2, code="2", namespace=ns)
        PropertyFactory(concept=concept2, value="Concept2")

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children().size(), 2)

        self.assertEqual(resp.pyquery(".concepts li:eq(0) a").text(),
                         'Concept1')
        self.assertEqual(resp.pyquery(".concepts li:eq(0) a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 1}))
                         )
        self.assertEqual(resp.pyquery(".concepts li:eq(1) a").text(),
                         'Concept2')
        self.assertEqual(resp.pyquery(".concepts li:eq(1) a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )

    def test_letter_selected_filter_one_language(self):
        ns = NamespaceFactory(heading="Concepts")
        concept1 = ConceptFactory(id=1, code="1", namespace=ns)
        PropertyFactory(concept=concept1, value="A_Concept")
        concept2 = ConceptFactory(id=2, code="2", namespace=ns)
        PropertyFactory(concept=concept2, value="B_Concept")

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children().size(), 1)
        self.assertEqual(resp.pyquery(".concepts li a").text(),
                         'A_Concept')
        self.assertEqual(resp.pyquery(".concepts li a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 1}))
                         )

    def test_letter_selected_filter_two_concepts_two_languages(self):
        ns_concept = NamespaceFactory(id=2, heading="Concepts")
        spanish = LanguageFactory(code='es', name='Spanish')

        english_concept = ConceptFactory(id=1, code="1", namespace=ns_concept)
        PropertyFactory(concept=english_concept, value="A_EN_Concept")

        spanish_concept = ConceptFactory(id=2, code="2", namespace=ns_concept)
        PropertyFactory(concept=spanish_concept, language=spanish,
                        name="prefLabel", value="A_ES_Concept")

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children().size(), 1)
        self.assertEqual(resp.pyquery(".concepts li a").text(),
                         'A_EN_Concept')
        self.assertEqual(resp.pyquery(".concepts li a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 1}))
                         )

    def test_letter_selected_filter_one_concept_two_languages(self):
        ns_concept = NamespaceFactory(id=2, heading="Concepts")
        spanish = LanguageFactory(code='es', name='Spanish')

        concept = ConceptFactory(id=1, code="1", namespace=ns_concept)
        PropertyFactory(concept=concept, value="A_EN_Concept")
        PropertyFactory(concept=concept, language=spanish,
                        name="prefLabel", value="A_ES_Concept")

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery(".concepts").children().size(), 1)
        self.assertEqual(resp.pyquery(".concepts li a").text(),
                         'A_EN_Concept')
        self.assertEqual(resp.pyquery(".concepts li a").attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 1}))
                         )
