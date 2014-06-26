from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    ThemeFactory,
    GroupFactory,
)
from . import GemetTest, ERROR_404


class TestConceptView(GemetTest):
    def setUp(self):
        self.concept = TermFactory()
        PropertyFactory(concept=self.concept, name="prefLabel",
                        value="some prefLabel")
        PropertyFactory(concept=self.concept, name="definition",
                        value="some definition")
        PropertyFactory(concept=self.concept, name="scopeNote",
                        value="some scope note")

    def test_concept_one_theme(self):
        group = GroupFactory()
        theme = ThemeFactory()
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

        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.content p#definition').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.content p#scope-note').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('.content ul:eq(1) li a').text(),
                         "Group Parent")
        self.assertEqual(resp.pyquery('.content ul:eq(0) li a').text(),
                         "Theme Parent")

    def test_concept_two_themes(self):
        group = GroupFactory()
        theme1 = ThemeFactory(id=4, code="4")
        theme2 = ThemeFactory(id=5, code="5")

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

        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.content p#definition').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.content p#scope-note').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('.content ul:eq(1)').text(),
                         "Group Parent")
        themes = resp.pyquery('.content ul:eq(0) li a').text().split()
        self.assertEqual(len(themes), 2)
        self.assertEqual(themes[0], "ThemeP1")
        self.assertEqual(themes[1], "ThemeP2")

    def test_redirect(self):
        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content p:eq(2)').text()
        self.assertEqual(302, self.app.get(url).status_int)

    def test_404_error(self):
        url = reverse('concept', kwargs={'concept_id': 2, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
