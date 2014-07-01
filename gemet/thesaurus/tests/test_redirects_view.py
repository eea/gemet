from .factories import (
    LanguageFactory,
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
