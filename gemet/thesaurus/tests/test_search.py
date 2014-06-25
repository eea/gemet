from django.core.urlresolvers import reverse

from . import GemetTest
from .factories import (
    TermFactory,
    PropertyFactory,
    PropertyTypeFactory,
    RelationFactory,
)
from gemet.thesaurus.utils import SEPARATOR


class TestSearchView(GemetTest):
    def setUp(self):
        cp1 = TermFactory()
        cp2 = TermFactory(id=2, code='2')
        cp3 = TermFactory(id=3, code='3')
        cp11 = TermFactory(id=11, code='11')
        cp12 = TermFactory(id=12, code='12')
        cp13 = TermFactory(id=13, code='13')

        PropertyFactory(
            concept=cp1,
            value='{0}something{0}{0}not{0}hiddenLabel{0}'.format(SEPARATOR),
            name='searchText',
        )
        PropertyFactory(
            concept=cp2,
            value='{0}something else{0}altLabel{0}{0}{0}'.format(SEPARATOR),
            name='searchText',
        )
        PropertyFactory(
            concept=cp3,
            value='{0}another somefling{0}{0}{0}{0}'.format(SEPARATOR),
            name='searchText',
        )
        PropertyFactory(concept=cp11, value='broader 1')
        PropertyFactory(concept=cp12, value='broader 2.1')
        PropertyFactory(concept=cp13, value='broader 2.2')

        narrower = PropertyTypeFactory(name='narrower')
        broader = PropertyTypeFactory(id=2, name='broader')

        RelationFactory(source=cp1, target=cp11, property_type=broader)
        RelationFactory(source=cp11, target=cp1, property_type=narrower)
        RelationFactory(source=cp2, target=cp12, property_type=broader)
        RelationFactory(source=cp12, target=cp2, property_type=narrower)
        RelationFactory(source=cp2, target=cp13, property_type=broader)
        RelationFactory(source=cp13, target=cp2, property_type=narrower)

    def test_no_results(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = 'foo'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(len(resp.pyquery('.content li')), 0)
        self.assertEqual(resp.pyquery('.content .results-nr').text(),
                         '0 results found.')

    def test_multiple_results(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = 'something'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(len(resp.pyquery('.content ul > li')), 2)
        self.assertEqual(resp.pyquery('.content ul li:eq(0) a').text(),
                         'something')
        self.assertEqual(resp.pyquery('.content ul li:eq(1) a').text(),
                         'something else')

    def test_broader_context(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = 'something'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul > li').size(), 2)
        self.assertEqual(
            resp.pyquery('.content ul > li:eq(0) p').text(),
            'other names: not; hiddenLabel broader context: broader 1'
        )
        self.assertEqual(
            resp.pyquery('.content ul > li:eq(1) p').text(),
            'other names: altLabel broader context: broader 2.1; broader 2.2'
        )

    def test_number_of_results_found(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = 'something'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(len(resp.pyquery('.content li')), 2)
        self.assertEqual(resp.pyquery('.content .results-nr').text(),
                         '2 results found.')

    def test_regex_search(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = '%%some__ing'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(len(resp.pyquery('.content li')), 3)
        self.assertEqual(resp.pyquery('.content li:eq(0) a').text(),
                         'another somefling')
        self.assertEqual(resp.pyquery('.content li:eq(1) a').text(),
                         'something')
        self.assertEqual(resp.pyquery('.content li:eq(2) a').text(),
                         'something else')

    def test_other_names(self):
        url = reverse('search', kwargs={'langcode': 'en'})
        resp = self.app.get(url)
        form = resp.forms['search-form']
        form['query'] = '%%Label'
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(len(resp.pyquery('.content li')), 2)
        self.assertEqual(
            resp.pyquery('.content ul > li:eq(0) .py-other-names').text(),
            'not; hiddenLabel'
        )
        self.assertEqual(
            resp.pyquery('.content ul > li:eq(1) .py-other-names').text(),
            'altLabel'
        )
