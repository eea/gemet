from django.urls import reverse

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
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content table').size(), 0)

    def test_one_entry_all_data(self):
        DataSourceFactory(abbr="abbr", author="author", title="title",
                          url="url", publication="publication",
                          place="place", year="year")
        url = reverse('definition_sources',
                      kwargs={'langcode': self.language.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertTrue('author' in resp.pyquery('ol li').text())
        self.assertTrue('title' in resp.pyquery('ol li').text())
        self.assertTrue('url' in resp.pyquery('ol li').text())
        self.assertTrue('publication' in resp.pyquery('ol li').text())
        self.assertTrue('place' in resp.pyquery('ol li').text())
        self.assertTrue('year' in resp.pyquery('ol li').text())

    def test_one_entry_less_data(self):
        DataSourceFactory(abbr="abbr", url="url")
        url = reverse('definition_sources',
                      kwargs={'langcode': self.language.code})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('ol li').text(), 'url')
