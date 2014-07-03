from .factories import (
    LanguageFactory,
    ThemeFactory,
)
from . import GemetTest


class TestRedirectsView(GemetTest):
    def setUp(self):
        LanguageFactory()

    def test_index_html(self):
        resp = self.app.get('/index_html')

        self.assertEqual(301, resp.status_int)

    def test_groups(self):
        resp = self.app.get('/groups')

        self.assertEqual(301, resp.status_int)

    def test_index_html(self):
        theme = ThemeFactory()
        resp = self.app.get(u'/theme_concepts?th={th}&langcode={langcode}'
                            .format(
                                th = theme.id,
                                langcode='en-US',
                            ))
        self.assertEqual(301, resp.status_int)

    def test_alphabetic(self):
        resp = self.app.get(u'/alphabetic?letter={letter}&langcode={langcode}'
                            .format(
                                letter=1,
                                langcode='en-US',
                            ))
        self.assertEqual(301, resp.status_int)
