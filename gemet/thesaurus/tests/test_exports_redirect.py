from django_webtest import WebTest
from django.test.testcases import SimpleTestCase
from django.core.urlresolvers import reverse

from .factories import (
    LanguageFactory,
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    ThemeFactory,
    GroupFactory,
    SuperGroupFactory,
)
from . import GemetTest


class TestExports(GemetTest):
    def get_reverse(self, name, with_language=False):
        if with_language:
            return reverse(name, kwargs={'langcode': 'en'})
        else:
            return reverse(name)

    def get_resp(self, view_name):
        return self.app.get(
            reverse('redirects', kwargs={'view_name': view_name})
        )

    def setUp(self):
        LanguageFactory()

    def test_rdf(self):
        self.assertRedirects(
            self.get_resp('rdf'),
            self.get_reverse('download', with_language=True),
            status_code=301
        )

    def test_gemet_backbone_html(self):
        self.assertRedirects(
            self.get_resp('gemet-backbone.html'),
            self.get_reverse('gemet-backbone.html'),
            status_code=301
        )

    def test_gemet_backbone_rdf(self):
        self.assertRedirects(
            self.get_resp('gemet-backbone.rdf'),
            self.get_reverse('gemet-backbone.rdf'),
            status_code=301
        )

    def test_gemet_definitions_html(self):
        self.assertRedirects(
            self.get_resp('gemet-definitions.html'),
            self.get_reverse('gemet-definitions.html'),
            status_code=301
        )

    def test_gemet_groups_html(self):
        self.assertRedirects(
            self.get_resp('gemet-groups.html'),
            self.get_reverse('gemet-groups.html'),
            status_code=301
        )

    def test_gemet_relations(self):
        self.assertRedirects(
            self.get_resp('gemet-relations.html'),
            self.get_reverse('gemet-relations.html'),
            status_code=301
        )

    def test_gemet_skoscore(self):
        self.assertRedirects(
            self.get_resp('gemet-skoscore.rdf'),
            self.get_reverse('gemet-skoscore.rdf'),
            status_code=301
        )

    def test_gemet_thesaurus(self):
        self.assertRedirects(
            self.get_resp('gemetThesaurus'),
            self.get_reverse('gemetThesaurus'),
            status_code=301
        )

    def test_gemet_definitions_rdf(self):
        self.assertRedirects(
            self.get_resp('gemet-definitions.rdf'),
            self.get_reverse('gemet-definitions.rdf', with_language=True),
            status_code=301
        )

    def test_gemet_groups_rdf(self):
        self.assertRedirects(
            self.get_resp('gemet-groups.rdf'),
            self.get_reverse('gemet-groups.rdf', with_language=True),
            status_code=301
        )
