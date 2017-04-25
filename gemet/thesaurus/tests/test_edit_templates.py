from django.core.urlresolvers import reverse

from .factories import ForeignRelationFactory, GroupFactory, LanguageFactory
from .factories import PropertyFactory, PropertyTypeFactory, RelationFactory
from .factories import SuperGroupFactory, TermFactory, ThemeFactory, UserFactory
from gemet.thesaurus import DELETED_PENDING, PUBLISHED, PENDING
from . import GemetTest


class TestEditConceptView(GemetTest):
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
                        value="source new", status=PENDING)
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition').text(),
                         "definition new")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "scope note new")
        self.assertEqual(resp.pyquery('.content #source').text(),
                         "source new")

    def test_alternatives(self):
        PropertyFactory(concept=self.concept, name="altLabel",
                        value="alternativeold", status=PUBLISHED)
        PropertyFactory(concept=self.concept, name="altLabel",
                        value="alternativenew", status=PENDING)
        PropertyFactory(concept=self.concept, name="altLabel",
                        value="alternativedeleted", status=DELETED_PENDING)
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(len(resp.pyquery('.alternative-item span')), 3)

    def test_relations(self):
        self.group = GroupFactory()
        self.theme = ThemeFactory()
        self.other_theme = ThemeFactory()
        PropertyFactory(concept=self.group, value="Group",
                        status=PUBLISHED)
        PropertyFactory(concept=self.theme, value="Theme",
                        status=PUBLISHED)
        PropertyFactory(concept=self.other_theme, value='Other_theme',
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
        RelationFactory(property_type=pt2, source=self.concept,
                        target=self.other_theme, status=DELETED_PENDING)
        RelationFactory(property_type=pt4, source=self.other_theme,
                        target=self.concept, status=DELETED_PENDING)
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        deleted_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-3').text().split()[0]
        pending_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-0').text().split()[0]
        published_relation = resp.pyquery('ul.listing:eq(1) div').children(
            '.status-1').text().split()[0]
        self.assertEqual(deleted_relation, "Other_theme")
        self.assertEqual(pending_relation, "Theme")
        self.assertEqual(published_relation, "Group")

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
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        themes_displayed = resp.pyquery(
            'ul.listing:eq(0) div').children('.status-0')
        self.assertEqual(len(themes_displayed), 1)
        self.assertEqual(themes_displayed.text().split()[0], "ThemeNew")

    def test_related_concepts(self):
        self.other_concept = TermFactory(code=u'99')
        self.concept3 = TermFactory(code=u'200')
        PropertyFactory(concept=self.other_concept, value="OtherConcept",
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept3, value="Concept3",
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.other_concept, status=PENDING)
        RelationFactory(property_type=pt1, source=self.other_concept,
                        target=self.concept, status=PENDING)
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.concept3, status=DELETED_PENDING)
        RelationFactory(property_type=pt1, source=self.concept3,
                        target=self.concept, status=DELETED_PENDING)
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        deleted_relation = resp.pyquery(
            '.elements-list li.status-3').text().split()[0]
        pending_relation = resp.pyquery(
            '.elements-list li.status-0').text().split()[0]
        self.assertEqual(deleted_relation, "Concept3")
        self.assertEqual(pending_relation, "OtherConcept")

    def test_related_concepts_with_new_concept(self):
        self.other_concept = TermFactory(code=u'101')
        PropertyFactory(concept=self.other_concept, value="OtherConcept",
                        status=PENDING)
        pt1 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.other_concept, status=PUBLISHED)
        RelationFactory(property_type=pt1, source=self.other_concept,
                        target=self.concept, status=PUBLISHED)
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        published_relation = resp.pyquery(
            '.elements-list li.status-1').text().split()[0]
        self.assertEqual(published_relation, "OtherConcept")

    def test_foreign_relations(self):
        pt1 = PropertyTypeFactory(name="HasCloseMatch", label="Has close match")
        ForeignRelationFactory(property_type=pt1, concept=self.concept,
                               status=PUBLISHED, uri='www.ds.com',
                               label='Oldexternal')
        ForeignRelationFactory(property_type=pt1, concept=self.concept,
                               status=PENDING, uri='www.ds.com',
                               label='Newexternal')
        ForeignRelationFactory(property_type=pt1, concept=self.concept,
                               status=DELETED_PENDING, uri='www.ds.com',
                               label='Deletedexternal')
        url = reverse('concept_edit', kwargs={'code': self.concept.code,
                                              'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        foreign_displayed = resp.pyquery('.other-item a').text().split()
        self.assertEqual(len(foreign_displayed), 3)
        self.assertEqual(resp.pyquery('.status-1.other-item a').text(),
                         'Oldexternal')
        self.assertEqual(resp.pyquery('.status-0.other-item a').text(),
                         'Newexternal')
        self.assertEqual(resp.pyquery('.status-3.other-item a').text(),
                         'Deletedexternal')


class TestEditGroupView(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        user = UserFactory()
        LanguageFactory()
        self.user = user.username

    def test_properties(self):
        PropertyFactory(concept=self.group, name="prefLabel",
                        value="prefLabel", status=DELETED_PENDING)
        PropertyFactory(concept=self.group, name="prefLabel",
                        value="prefLabel new", status=PENDING)
        PropertyFactory(concept=self.group, name="definition",
                        value="definition", status=DELETED_PENDING)
        PropertyFactory(concept=self.group, name="definition",
                        value="definition new", status=PENDING)
        url = reverse('group_edit', kwargs={'code': self.group.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition').text(),
                         "definition new")

    def test_relations(self):
        self.supergroup = SuperGroupFactory()
        self.concept = TermFactory()
        self.other_supergroup = SuperGroupFactory()
        PropertyFactory(concept=self.supergroup, value="SuperGroup",
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept, value="Concept",
                        status=PUBLISHED)
        PropertyFactory(concept=self.other_supergroup,
                        value='Other_supergroup',
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="broader", label="Broader")
        pt3 = PropertyTypeFactory(name="group", label="Group")
        pt4 = PropertyTypeFactory(name="narrower", label="Narrower")

        RelationFactory(property_type=pt1, source=self.group,
                        target=self.concept, status=PUBLISHED)
        RelationFactory(property_type=pt2, source=self.group,
                        target=self.supergroup, status=PENDING)
        RelationFactory(property_type=pt3, source=self.concept,
                        target=self.group, status=PUBLISHED)
        RelationFactory(property_type=pt4, source=self.supergroup,
                        target=self.group, status=PENDING)
        RelationFactory(property_type=pt2, source=self.group,
                        target=self.other_supergroup, status=DELETED_PENDING)
        RelationFactory(property_type=pt4, source=self.other_supergroup,
                        target=self.group, status=DELETED_PENDING)
        url = reverse('group_edit', kwargs={'code': self.group.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        deleted_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-3').text().split()[0]
        pending_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-0').text().split()[0]
        published_relation = resp.pyquery('ul.listing:eq(1) div').children(
            '.status-1').text().split()[0]
        self.assertEqual(deleted_relation, "Other_supergroup")
        self.assertEqual(pending_relation, "SuperGroup")
        self.assertEqual(published_relation, "Concept")

    def test_user_sees_concept_default_name(self):
        LanguageFactory(code='ro')
        concept4 = TermFactory(code="4", status=PUBLISHED)
        PropertyFactory(concept=concept4, value="Concept4", status=PUBLISHED)
        PropertyFactory(concept=concept4, value='',
                        language__code='ro',
                        status=PUBLISHED)
        url = reverse('concept_edit', kwargs={'langcode': 'ro',
                                              'code': 4})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('title').text(),
                         'Edit Concept4 [english]')
        self.assertEqual(resp.pyquery('#parent-prefLabel').text(),
                         '')


class TestEditSuperGroupView(GemetTest):
    def setUp(self):
        self.supergroup = SuperGroupFactory()
        user = UserFactory()
        LanguageFactory()
        self.user = user.username

    def test_properties(self):
        PropertyFactory(concept=self.supergroup, name="prefLabel",
                        value="prefLabel", status=DELETED_PENDING)
        PropertyFactory(concept=self.supergroup, name="prefLabel",
                        value="prefLabel new", status=PENDING)
        PropertyFactory(concept=self.supergroup, name="definition",
                        value="definition", status=DELETED_PENDING)
        PropertyFactory(concept=self.supergroup, name="definition",
                        value="definition new", status=PENDING)
        PropertyFactory(concept=self.supergroup, name="scopeNote",
                        value="scope note", status=DELETED_PENDING)
        PropertyFactory(concept=self.supergroup, name="scopeNote",
                        value="scope note new", status=PENDING)
        url = reverse('supergroup_edit', kwargs={'code': self.supergroup.code,
                                                 'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition').text(),
                         "definition new")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "scope note new")

    def test_relations(self):
        self.group1 = GroupFactory()
        self.group2 = GroupFactory(code=u'33')
        self.group3 = GroupFactory(code=u'34')
        PropertyFactory(concept=self.supergroup,
                        value="SuperGroup",
                        status=PUBLISHED)
        PropertyFactory(concept=self.group1,
                        value="Group1",
                        status=PUBLISHED)
        PropertyFactory(concept=self.group2,
                        value='Group2',
                        status=PUBLISHED)
        PropertyFactory(concept=self.group3,
                        value='Group3',
                        status=PUBLISHED)

        pt1 = PropertyTypeFactory(name="narrower", label="Narrower")
        pt2 = PropertyTypeFactory(name="broader", label="Broader")

        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=self.group1, status=PUBLISHED)
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=self.group2, status=PENDING)
        RelationFactory(property_type=pt2, source=self.group1,
                        target=self.supergroup, status=PUBLISHED)
        RelationFactory(property_type=pt2, source=self.group2,
                        target=self.supergroup, status=PENDING)
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=self.group3, status=DELETED_PENDING)
        RelationFactory(property_type=pt2, source=self.group3,
                        target=self.supergroup, status=DELETED_PENDING)
        url = reverse('supergroup_edit', kwargs={'code': self.supergroup.code,
                                                 'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        deleted_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-3').text().split()[0]
        pending_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-0').text().split()[0]
        published_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-1').text().split()[0]

        self.assertEqual(deleted_relation, "Group3")
        self.assertEqual(pending_relation, "Group2")
        self.assertEqual(published_relation, "Group1")


class TestEditThemeView(GemetTest):
    def setUp(self):
        self.theme = ThemeFactory()
        user = UserFactory()
        LanguageFactory()
        self.user = user.username

    def test_properties(self):
        PropertyFactory(concept=self.theme, name="prefLabel",
                        value="prefLabel", status=DELETED_PENDING)
        PropertyFactory(concept=self.theme, name="prefLabel",
                        value="prefLabel new", status=PENDING)
        PropertyFactory(concept=self.theme, name="definition",
                        value="definition", status=DELETED_PENDING)
        PropertyFactory(concept=self.theme, name="definition",
                        value="definition new", status=PENDING)
        PropertyFactory(concept=self.theme, name="scopeNote",
                        value="scope note", status=DELETED_PENDING)
        PropertyFactory(concept=self.theme, name="scopeNote",
                        value="scope note new", status=PENDING)
        url = reverse('theme_edit', kwargs={'code': self.theme.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition').text(),
                         "definition new")
        self.assertEqual(resp.pyquery('.content #scopeNote').text(),
                         "scope note new")

    def test_relations(self):
        self.concept1 = TermFactory()
        self.concept2 = TermFactory(code=u'33')
        self.concept3 = TermFactory(code=u'34')
        PropertyFactory(concept=self.theme,
                        value="Theme",
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept1,
                        value="Concept1",
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept2,
                        value='Concept2',
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept3,
                        value='Concept3',
                        status=PUBLISHED)

        pt1 = PropertyTypeFactory(name="themeMember", label="ThemeMember")
        pt2 = PropertyTypeFactory(name="theme", label="Theme")

        RelationFactory(property_type=pt1, source=self.theme,
                        target=self.concept1, status=PUBLISHED)
        RelationFactory(property_type=pt1, source=self.theme,
                        target=self.concept2, status=PENDING)
        RelationFactory(property_type=pt2, source=self.concept1,
                        target=self.theme, status=PUBLISHED)
        RelationFactory(property_type=pt2, source=self.concept2,
                        target=self.theme, status=PENDING)
        RelationFactory(property_type=pt1, source=self.theme,
                        target=self.concept3, status=DELETED_PENDING)
        RelationFactory(property_type=pt2, source=self.concept3,
                        target=self.theme, status=DELETED_PENDING)
        url = reverse('theme_edit', kwargs={'code': self.theme.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        deleted_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-3').text().split()[0]
        pending_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-0').text().split()[0]
        published_relation = resp.pyquery('ul.listing:eq(0) div').children(
            '.status-1').text().split()[0]

        self.assertEqual(deleted_relation, "Concept3")
        self.assertEqual(pending_relation, "Concept2")
        self.assertEqual(published_relation, "Concept1")


class TestDefinitionEmpty(GemetTest):
    def setUp(self):
        self.language = LanguageFactory(code='ro')
        self.concept = TermFactory(code='200', status=PUBLISHED)
        PropertyFactory(concept=self.concept, id=1234, name='definition',
                        language__code='en', value='English definition')
        user = UserFactory()
        self.user = user.username

    def test_check_default_definition_does_not_appear_on_edit_page(self):
        url = reverse('concept_edit', kwargs={'langcode': self.language.code,
                                               'code': self.concept.code
                                               })
        response = self.app.get(url, user=self.user)
        self.assertEqual(response.pyquery(' #parent-definition').text(), '')

    def test_check_definition_for_language_appears_on_edit_page(self):
        PropertyFactory(concept=self.concept, id=1235, name='definition',
                        language__code='ro', value='Romanian definition')

        url = reverse('concept_edit', kwargs={'langcode': self.language.code,
                                              'code': self.concept.code
                                              })
        response = self.app.get(url, user=self.user)
        self.assertEqual(response.pyquery(' #parent-definition').text(),
                         'Romanian definition')
