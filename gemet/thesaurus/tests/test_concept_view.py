from django.core.urlresolvers import reverse
from django.conf import settings

from .factories import ForeignRelationFactory, GroupFactory, LanguageFactory
from .factories import PropertyFactory, PropertyTypeFactory, RelationFactory
from .factories import TermFactory, ThemeFactory, UserFactory
from gemet.thesaurus import DELETED_PENDING, PUBLISHED, PENDING
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

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.group)
        RelationFactory(property_type=pt1, source=self.group,
                        target=self.concept)

        pt3 = PropertyTypeFactory(name="themeMember", label="Theme member")
        pt4 = PropertyTypeFactory(name="theme", label="Theme")
        RelationFactory(property_type=pt4, source=self.concept,
                        target=self.theme)
        RelationFactory(property_type=pt3, source=self.theme,
                        target=self.concept)

    def set_concept_two_theme(self):
        self.group = GroupFactory()
        self.theme1 = ThemeFactory(code="4")
        self.theme2 = ThemeFactory(code="5")

        PropertyFactory(concept=self.group, value="Group Parent")
        PropertyFactory(concept=self.theme1, value="ThemeP1")
        PropertyFactory(concept=self.theme2, value="ThemeP2")

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.group)
        RelationFactory(property_type=pt1, source=self.group,
                        target=self.concept)

        pt3 = PropertyTypeFactory(name="themeMember",
                                  label="Theme member")
        pt4 = PropertyTypeFactory(name="theme", label="Theme")
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
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "some prefLabel")
        self.assertEqual(resp.pyquery('.content #definition p').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('ul.listing:eq(1) li').text(),
                         "Group Parent")
        self.assertEqual(resp.pyquery('ul.listing:eq(0) li').text(),
                         "Theme Parent")

    def test_concept_one_theme_rdf(self):
        self.set_concept_one_theme()
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, extra_environ={
            'HTTP_ACCEPT': 'application/rdf+xml'
        })

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.headers['Content-Type'], 'application/rdf+xml')
        self.assertEqual(resp.body.count('concept/' + self.concept.code), 1)
        self.assertEqual(resp.body.count('group/' + self.group.code), 1)
        self.assertEqual(resp.body.count('theme/' + self.theme.code), 1)

    def test_concept_two_themes(self):
        self.set_concept_two_theme()
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "some prefLabel")
        self.assertEqual(resp.pyquery('.content #definition p').text(),
                         "some definition")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "some scope note")
        self.assertEqual(resp.pyquery('ul.listing:eq(1)').text(),
                         "Group Parent")
        themes = resp.pyquery('ul.listing:eq(0) li').text().split()
        self.assertEqual(len(themes), 2)
        self.assertEqual(themes[0], "ThemeP1")
        self.assertEqual(themes[1], "ThemeP2")

    def test_concept_two_themes_rdf(self):
        self.set_concept_two_theme()
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, extra_environ={
            'HTTP_ACCEPT': 'application/rdf+xml'
        })

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.headers['Content-Type'], 'application/rdf+xml')
        self.assertEqual(resp.body.count('concept/' + self.concept.code), 1)
        self.assertEqual(resp.body.count('group/' + self.group.code), 1)
        self.assertEqual(resp.body.count('theme/' + self.theme1.code), 1)
        self.assertEqual(resp.body.count('theme/' + self.theme2.code), 1)

    def test_redirect(self):
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content h5.h5-url').text().split()[-1]
        self.assertTrue(settings.GEMET_URL in url)
        self.assertTrue(url.endswith(self.concept.code))

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
        url = reverse('concept', kwargs={'code': 2, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())


class TestConceptViewWithUser(GemetTest):
    def setUp(self):
        self.concept = TermFactory()
        user = UserFactory()
        LanguageFactory()
        self.user = user.username

    def test_properties(self):
        PropertyFactory(concept=self.concept, name="prefLabel",
                        value="prefLabel", status=DELETED_PENDING)
        PropertyFactory(concept=self.concept, name="prefLabel",
                        value="prefLabel new", status=PENDING)
        PropertyFactory(concept=self.concept, name="definition",
                        value="definition", status=DELETED_PENDING)
        PropertyFactory(concept=self.concept, name="definition",
                        value="definition new", status=PENDING)
        PropertyFactory(concept=self.concept, name="scopeNote",
                        value="scope note", status=DELETED_PENDING)
        PropertyFactory(concept=self.concept, name="scopeNote",
                        value="scope note new", status=PENDING)
        PropertyFactory(concept=self.concept, name="source",
                        value="source", status=DELETED_PENDING)
        PropertyFactory(concept=self.concept, name="source",
                        value="source new", status=DELETED_PENDING)
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition p').text(),
                         "definition new")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "scope note new")

    def test_alternatives(self):
        PropertyFactory(concept=self.concept, name="altLabel",
                        value="alternativeold", status=PUBLISHED)
        PropertyFactory(concept=self.concept, name="altLabel",
                        value="alternativenew", status=PENDING)
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        alternatives_displayed = resp.pyquery('.alternatives').text().split()
        self.assertEqual(len(alternatives_displayed), 2)
        self.assertEqual(alternatives_displayed[0], "alternativeold;")
        self.assertEqual(alternatives_displayed[1], "alternativenew;")

    def test_relations(self):
        self.group = GroupFactory()
        self.theme = ThemeFactory()
        PropertyFactory(concept=self.group, value="Group",
                        status=PUBLISHED)
        PropertyFactory(concept=self.theme, value="Theme",
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="group", label="Group")
        pt2 = PropertyTypeFactory(name="theme", label="Theme")
        pt3 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt4 = PropertyTypeFactory(name="themeMember", label="Theme member")

        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.group, status=PUBLISHED)
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.theme, status=PENDING)
        RelationFactory(property_type=pt3, source=self.group,
                        target=self.concept, status=PUBLISHED)
        RelationFactory(property_type=pt4, source=self.theme,
                        target=self.concept, status=PENDING)

        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        themes_displayed = resp.pyquery('ul.listing:eq(0)').text().split()
        groups_displayed = resp.pyquery('ul.listing:eq(1)').text().split()
        self.assertEqual(len(themes_displayed), 1)
        self.assertEqual(len(groups_displayed), 1)
        self.assertEqual(themes_displayed[0], "Theme")
        self.assertEqual(groups_displayed[0], "Group")

    # todo fix the problem in the app
    def test_relation_with_pending_name(self):
        self.theme = ThemeFactory()
        PropertyFactory(concept=self.theme, value="ThemeOld",
                        status=DELETED_PENDING)
        PropertyFactory(concept=self.theme, value="ThemeNew",
                        status=PENDING)
        pt1 = PropertyTypeFactory(name="theme", label="Theme")
        pt2 = PropertyTypeFactory(name="themeMember", label="Theme member")
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.theme, status=PENDING)
        RelationFactory(property_type=pt2, source=self.theme,
                        target=self.concept, status=PENDING)
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        themes_displayed = resp.pyquery('ul.listing:eq(0)').text().split()
        self.assertEqual(len(themes_displayed), 1)
        self.assertEqual(themes_displayed[0], "ThemeNew")

    def test_related_concepts(self):
        self.other_concept = TermFactory(code=u'99')
        PropertyFactory(concept=self.other_concept, value="OtherConcept",
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.other_concept, status=PENDING)
        RelationFactory(property_type=pt1, source=self.other_concept,
                        target=self.concept, status=PENDING)
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        related_displayed = resp.pyquery('ul.listing:eq(0)').text().split()
        self.assertEqual(len(related_displayed), 1)
        self.assertEqual(related_displayed[0], "OtherConcept")

    def test_related_concepts_with_new_concept(self):
        self.other_concept = TermFactory(code=u'101')
        PropertyFactory(concept=self.other_concept, value="OtherConcept",
                        status=PENDING)
        pt1 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.other_concept,
                        target=self.concept, status=PENDING)
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.other_concept, status=PENDING)
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        related_displayed = resp.pyquery('ul.listing:eq(0)').text().split()
        self.assertEqual(len(related_displayed), 1)
        self.assertEqual(related_displayed[0], "OtherConcept")

    def test_foreign_relations(self):
        pt1 = PropertyTypeFactory(name="HasCloseMatch", label="Has close match")
        ForeignRelationFactory(property_type=pt1, concept=self.concept,
                               status=PUBLISHED, uri='www.ds.com',
                               label='Oldexternal')
        ForeignRelationFactory(property_type=pt1, concept=self.concept,
                               status=PENDING, uri='www.ds.com',
                               label='Newexternal')
        url = reverse('concept', kwargs={'code': self.concept.code,
                                         'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        foreign_displayed = resp.pyquery('li.inline a').text().split()
        self.assertEqual(len(foreign_displayed), 2)

    def test_user_sees_default_name(self):
        LanguageFactory(code='ro')
        concept4 = TermFactory(code="4", status=PUBLISHED)
        PropertyFactory(concept=concept4, value="Concept4", status=PUBLISHED)
        PropertyFactory(concept=concept4, value='',
                        language__code='ro',
                        status=PUBLISHED)
        url = reverse('concept', kwargs={'langcode': 'ro',
                                         'code': concept4.code})
        resp = self.app.get(url)
        self.assertEqual(resp.pyquery('title').text(), 'Concept4 [english]')
        self.assertEqual(resp.pyquery('#prefLabel').text(),
                         'Concept4 [english]')
