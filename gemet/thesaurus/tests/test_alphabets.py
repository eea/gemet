from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    LanguageFactory,
)


class TestAlphabetsView(WebTest):

    def test_english_letters(self):
        LanguageFactory()

        url = reverse('alphabets', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ol').children().size(), 26)
        letters = resp.pyquery('ol').text().split()
        self.assertEqual(letters[0], 'a')
        self.assertEqual(letters[1], 'A')
        self.assertEqual(letters[50], 'z')
        self.assertEqual(letters[51], 'Z')
