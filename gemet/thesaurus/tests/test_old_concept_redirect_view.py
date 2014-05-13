from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    PropertyTypeFactory,
    RelationFactory,
    TermFactory,
    ThemeFactory,
    GroupFactory,
    SuperGroupFactory,
)
from . import GemetTest


class TestOldConceptRedirectView(GemetTest):
    def test_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=concept.id)
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
                      cp=concept.id)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)

    def test_404_no_concept(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=5)
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)

    def test_404_no_language(self):
        concept = TermFactory()
        PropertyFactory(concept=concept)

        url = "{url}?langcode={lang}&ns={ns}&cp={cp}"\
              .format(url=reverse('old_concept_redirect'),
                      ns=concept.namespace.id,
                      cp=concept.code,
                      lang='ESP')
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)