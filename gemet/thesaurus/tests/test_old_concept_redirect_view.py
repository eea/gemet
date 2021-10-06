from django.urls import reverse

from .factories import (
    PropertyFactory,
    TermFactory,
    ThemeFactory,
    GroupFactory,
    SuperGroupFactory,
)
from . import GemetTest, ERROR_404


class TestOldConceptRedirectView(GemetTest):
    def test_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=concept.code)
        resp = self.app.get(url)

        self.assertEqual(302, resp.status_int)
        self.assertEqual(200, resp.follow().status_int)

    def test_theme(self):
        theme = ThemeFactory()
        PropertyFactory(concept=theme)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=theme.namespace.id,
                      cp=theme.code)
        resp = self.app.get(url)

        self.assertEqual(302, resp.status_int)
        self.assertEqual(200, resp.follow().status_int)

    def test_group(self):
        group = GroupFactory()
        PropertyFactory(concept=group)
        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=group.namespace.id,
                      cp=group.code)
        resp = self.app.get(url)

        self.assertEqual(302, resp.status_int)
        self.assertEqual(200, resp.follow().status_int)

    def test_supergroup(self):
        supergroup = SuperGroupFactory()
        PropertyFactory(concept=supergroup)
        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=supergroup.namespace.id,
                      cp=supergroup.code)
        resp = self.app.get(url)

        self.assertEqual(302, resp.status_int)
        self.assertEqual(200, resp.follow().status_int)

    def test_language(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)
        url = "{url}?langcode={lang}&ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=concept.code,
                      lang='en')
        resp = self.app.get(url)

        self.assertEqual(302, resp.status_int)
        self.assertEqual(200, resp.follow().status_int)

    def test_404_no_namespace(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=5,
                      cp=concept.code)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_no_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=5)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_no_ns_parameter(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      cp=concept.code)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_no_cp_parameter(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_no_language(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?langcode={lang}&ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=concept.code,
                      lang='ESP')
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(302, resp.status_int)
        resp = resp.follow(expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_no_concept_type(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?langcode={lang}&ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=7,
                      cp=concept.code,
                      lang='en')
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
