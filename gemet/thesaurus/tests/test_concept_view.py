from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestConceptView(WebTest):
    def setUp(self):
        self.ns_concept = NamespaceFactory(id=1, heading="Concept")
        self.concept = ConceptFactory(namespace=self.ns_concept)
        PropertyFactory(concept=self.concept, name="prefLabel",
                        value="some prefLabel")
        PropertyFactory(concept=self.concept, name="definition",
                        value="some definition")
        PropertyFactory(concept=self.concept, name="scopeNote",
                        value="some scope note")

    def test_one_theme_concept(self):
        ns_group = NamespaceFactory(id=2, heading="Group")
        ns_theme = NamespaceFactory(id=4, heading="Themes")
        group = ConceptFactory(id=2, code="2", namespace=ns_group)
        theme = ConceptFactory(id=3, code="3", namespace=ns_theme)
        PropertyFactory(concept=group, value="Group Parent")
        PropertyFactory(concept=theme, value="Theme Parent")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept, target=group)
        RelationFactory(property_type=pt1, source=group, target=self.concept)

        pt3 = PropertyTypeFactory(id=3, name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(id=4, name="theme", label="Theme")
        RelationFactory(property_type=pt4, source=self.concept,
                        target=theme)
        RelationFactory(property_type=pt3, source=theme, target=self.concept)

        url = reverse('concept', kwargs={'concept_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.infotext:eq(0)').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.infotext:eq(1)').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('.infotext:eq(2)').text(),
                         "Group Parent")
        self.assertEqual(resp.pyquery('.infotext:eq(3)').text(),
                         "Theme Parent")

    def test_two_themes_concept(self):
        ns_group = NamespaceFactory(id=2, heading="Group")
        ns_theme = NamespaceFactory(id=4, heading="Themes")
        group = ConceptFactory(id=2, code="2", namespace=ns_group)
        theme1 = ConceptFactory(id=3, code="3", namespace=ns_theme)
        theme2 = ConceptFactory(id=4, code="4", namespace=ns_theme)

        PropertyFactory(concept=group, value="Group Parent")
        PropertyFactory(concept=theme1, value="ThemeP1")
        PropertyFactory(concept=theme2, value="ThemeP2")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept, target=group)
        RelationFactory(property_type=pt1, source=group, target=self.concept)

        pt3 = PropertyTypeFactory(id=3, name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(id=4, name="theme", label="Theme")
        RelationFactory(property_type=pt4, source=self.concept,
                        target=theme1)
        RelationFactory(property_type=pt3, source=theme1, target=self.concept)
        RelationFactory(property_type=pt4, source=self.concept,
                        target=theme2)
        RelationFactory(property_type=pt3, source=theme2, target=self.concept)

        url = reverse('concept', kwargs={'concept_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.infotext:eq(0)').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.infotext:eq(1)').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('.infotext:eq(2)').text(),
                         "Group Parent")
        themes = resp.pyquery('.infotext:eq(3)').text().split()
        self.assertEqual(len(themes), 2)
        self.assertEqual(themes[0], "ThemeP1")
        self.assertEqual(themes[1], "ThemeP2")

    def test_404_error(self):
        url = reverse('concept', kwargs={'concept_id': 2, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
