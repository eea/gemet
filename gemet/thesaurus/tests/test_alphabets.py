from django_webtest import WebTest
from django.core.urlresolvers import reverse

from gemet.thesaurus.collation_charts import unicode_character_map
from .factories import (
    LanguageFactory,
)


class TestAlphabetsView(WebTest):

    def test_english_letters(self):
        LanguageFactory()

        url = reverse('alphabets', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        letters = unicode_character_map.get('en', [])

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('ul').children().size(), 26)
        first_row = resp.pyquery('.letter:first').text().split()
        self.assertEqual(first_row[0], '1')
        self.assertEqual(first_row[1], 'a')
        self.assertEqual(first_row[2], 'A')
        last_row = resp.pyquery('.letter:last').text().split()
        self.assertEqual(last_row[0], '26')
        self.assertEqual(last_row[1], 'z')
        self.assertEqual(last_row[2], 'Z')
