import unittest
from django.core.urlresolvers import reverse

from .factories import LanguageFactory, PropertyFactory, TermFactory
from .factories import VersionFactory
from . import GemetTest, ERROR_404


class TestAlphabeticView(GemetTest):
    def setUp(self):
        LanguageFactory()
        VersionFactory()

    def test_no_concepts(self):
        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content li').size(), 0)

    def test_one_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'administration')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0) a')
                         .attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept.code})
                         )

    @unittest.skip('When a property in a certain language is missing, '
                   'that entry does not exist in the database. The case when '
                   'it exists with an empty value is unrealistic.')
    def test_two_languages_one_preflabel(self):
        concept = TermFactory()
        spanish = LanguageFactory(code='es', name='Spanish')
        PropertyFactory(concept=concept)
        PropertyFactory(concept=concept, name='prefLabel', value='',
                        language=spanish)

        url = reverse('alphabetic', kwargs={'langcode': spanish.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, spanish.code)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'administration [english]')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': spanish.code,
                                       'code': concept.code})
        )

    def test_more_concepts(self):
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value="Concept1")
        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value="Concept2")

        url = reverse('alphabetic', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 2)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         'Concept1')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0) a')
                         .attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept1.code})
                         )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(1)').text(),
                         'Concept2')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(1) a')
                         .attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept2.code})
                         )

    def test_letter_selected_filter_one_language(self):
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value="A_Concept")
        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value="B_Concept")

        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter=1)
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'A_Concept')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li a').attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept1.code})
                         )

    def test_wrong_letter_selected(self):
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value="A_Concept")
        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value="B_Concept")

        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter='lw')

        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_other_selected(self):
        concept1 = TermFactory(code="1")
        PropertyFactory(concept=concept1, value='"A_Concept"')
        concept2 = TermFactory(code="2")
        PropertyFactory(concept=concept2, value='"B_Concept"')

        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter=99)
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 2)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(0)').text(),
                         '"A_Concept"')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(0) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept1.code})
        )
        self.assertEqual(resp.pyquery('.content ul:eq(0) li:eq(1)').text(),
                         '"B_Concept"')
        self.assertEqual(
            resp.pyquery('.content ul:eq(0) li:eq(1) a').attr('href'),
            reverse('concept', kwargs={'langcode': 'en',
                                       'code': concept2.code})
        )

    def test_letter_selected_filter_two_concepts_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')

        english_concept = TermFactory(code="1")
        PropertyFactory(concept=english_concept, value="A_EN_Concept")

        spanish_concept = TermFactory(code="2")
        PropertyFactory(concept=spanish_concept, language=spanish,
                        name="prefLabel", value="A_ES_Concept")

        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter=1)
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'A_EN_Concept')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li a').attr('href'),
                         reverse('concept',
                                 kwargs={'langcode': 'en',
                                         'code': english_concept.code})
                         )

    def test_letter_selected_filter_one_concept_two_languages(self):
        spanish = LanguageFactory(code='es', name='Spanish')

        concept = TermFactory()
        PropertyFactory(concept=concept, value="A_EN_Concept")
        PropertyFactory(concept=concept, language=spanish,
                        name="prefLabel", value="A_ES_Concept")

        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter=1)
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         'A_EN_Concept')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li a').attr('href'),
                         reverse('concept', kwargs={'langcode': 'en',
                                                    'code': concept.code})
                         )

    def test_404_error_letter_out_of_range(self):
        url = '{url}?letter={letter}'\
              .format(url=reverse('alphabetic', kwargs={'langcode': 'en'}),
                      letter=100)
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
