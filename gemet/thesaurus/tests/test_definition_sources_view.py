from django.core.urlresolvers import reverse

from .factories import (
    LanguageFactory,
    DataSourceFactory,
)
from . import GemetTest


class TestDefinitionSourcesView(GemetTest):
    def setUp(self):
        self.language = LanguageFactory()

    def test_no_entry(self):
        url = reverse('definition_sources',
                      kwargs={'langcode': self.language.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content table').size(), 0)

    def test_one_entry_all_data(self):
        ds = DataSourceFactory(abbr="abbr", author="author", title="title",
                               url="url", publication="publication",
                               place="place", year="year")
        url = reverse('definition_sources',
                      kwargs={'langcode': self.language.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content table').size(), 1)
        self.assertEqual(
            resp.pyquery('.content table tr:eq(0) td:eq(1)').text(),
            "abbr")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(1) td:eq(1)').text(),
            "author")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(2) td:eq(1)').text(),
            "title")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(3) td:eq(1)').text(),
            "url")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(4) td:eq(1)').text(),
            "publication")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(5) td:eq(1)').text(),
            "place")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(6) td:eq(1)').text(),
            "year")

    def test_one_entry_all_data(self):
        ds = DataSourceFactory(abbr="abbr", url="url")
        url = reverse('definition_sources',
                      kwargs={'langcode': self.language.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content table').size(), 1)
        self.assertEqual(resp.pyquery('.content table tr').size(), 2)
        self.assertEqual(
            resp.pyquery('.content table tr:eq(0) td:eq(1)').text(),
            "abbr")
        self.assertEqual(
            resp.pyquery('.content table tr:eq(1) td:eq(1)').text(),
            "url")
