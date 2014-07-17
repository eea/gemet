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

    def set_concept_one_theme(self):
        self.group = GroupFactory()
        self.theme = ThemeFactory()
        PropertyFactory(concept=self.group, value="Group Parent")
        PropertyFactory(concept=self.theme, value="Theme Parent")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.group)
        RelationFactory(property_type=pt1, source=self.group,
                        target=self.concept)

        pt3 = PropertyTypeFactory(id=3, name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(id=4, name="theme", label="Theme")
        RelationFactory(property_type=pt4, source=self.concept,
                        target=self.theme)
        RelationFactory(property_type=pt3, source=self.theme,
                        target=self.concept)

    def set_concept_two_theme(self):
        self.group = GroupFactory()
        self.theme1 = ThemeFactory(id=4, code="4")
        self.theme2 = ThemeFactory(id=5, code="5")

        PropertyFactory(concept=self.group, value="Group Parent")
        PropertyFactory(concept=self.theme1, value="ThemeP1")
        PropertyFactory(concept=self.theme2, value="ThemeP2")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.group)
        RelationFactory(property_type=pt1, source=self.group,
                        target=self.concept)

        pt3 = PropertyTypeFactory(id=3, name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(id=4, name="theme", label="Theme")
        RelationFactory(property_type=pt4, source=self.concept,
                        target=self.theme1)
        RelationFactory(property_type=pt3, source=self.theme1,
                        target=self.concept)
        RelationFactory(property_type=pt4, source=self.concept,
                        target=self.theme2)
        RelationFactory(property_type=pt3, source=self.theme2,
                        target=self.concept)

    def test_concept_one_theme(self):
        self.set_concept_one_theme()
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
        self.assertEqual(resp.pyquery('.content ul.listing:eq(1) li').text(),
                         "Group Parent")
        self.assertEqual(resp.pyquery('.content ul.listing:eq(0) li').text(),
                         "Theme Parent")

    def test_concept_one_theme_rdf(self):
        self.set_concept_one_theme()
        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url, extra_environ={
            'HTTP_ACCEPT': 'application/rdf+xml'
        })

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.headers['Content-Type'], 'application/rdf+xml')
        self.assertEqual(resp.body.count('concept/' + str(self.concept.id)), 1)
        self.assertEqual(resp.body.count('group/' + str(self.group.id)), 1)
        self.assertEqual(resp.body.count('theme/' + str(self.theme.id)), 1)

    def test_concept_two_themes(self):
        self.set_concept_two_theme()
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
        themes = resp.pyquery('.content ul.listing:eq(0) li').text().split()
        self.assertEqual(len(themes), 2)
        self.assertEqual(themes[0], "ThemeP1")
        self.assertEqual(themes[1], "ThemeP2")

    def test_concept_two_themes_rdf(self):
        self.set_concept_two_theme()
        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url, extra_environ={
            'HTTP_ACCEPT': 'application/rdf+xml'
        })

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.headers['Content-Type'], 'application/rdf+xml')
        self.assertEqual(resp.body.count('concept/' + str(self.concept.id)), 1)
        self.assertEqual(resp.body.count('group/' + str(self.group.id)), 1)
        self.assertEqual(resp.body.count('theme/' + str(self.theme1.id)), 1)
        self.assertEqual(resp.body.count('theme/' + str(self.theme2.id)), 1)

    def test_redirect(self):
        url = reverse('concept', kwargs={'concept_id': self.concept.id,
                                         'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content h5.h5-url').text().split()[-1] + '/'
        self.assertEqual(302, self.app.get(url).status_int)

    def test_redirect_rdf(self):
        url = reverse(
            'concept_redirect', kwargs={'concept_type': 'concept',
                                        'concept_code': self.concept.code}
        )
        resp = self.app.get(url, extra_environ={
            'HTTP_ACCEPT': 'application/rdf+xml'
        })
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.headers['Content-Type'], 'application/rdf+xml')

    def test_redirect_no_concept_type(self):
        url = reverse(
            'concept_redirect', kwargs={'concept_type': 'unknown',
                                        'concept_code': self.concept.code}
        )
        resp = self.app.get(url, expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())

    def test_404_error(self):
        url = reverse('concept', kwargs={'concept_id': 2, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
