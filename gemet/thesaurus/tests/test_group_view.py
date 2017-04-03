from django.core.urlresolvers import reverse
from django.conf import settings

from .factories import GroupFactory, LanguageFactory, PropertyFactory
from .factories import PropertyTypeFactory, RelationFactory, SuperGroupFactory
from .factories import TermFactory, UserFactory
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED
from . import GemetTest, ERROR_404


class TestGroupView(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, name="prefLabel",
                        value="some prefLabel")

    def test_group_no_concept(self):
        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "some prefLabel")
        self.assertEqual(resp.pyquery('.content p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         "English some prefLabel")

    def test_group_one_concept_one_supergroup(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, name="prefLabel",
                        value="concept prefLabel")
        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group,
                        target=concept)
        RelationFactory(property_type=pt2, source=concept,
                        target=self.group)

        supergroup = SuperGroupFactory()
        PropertyFactory(concept=supergroup, name="prefLabel",
                        value="supergroup prefLabel")
        pt3 = PropertyTypeFactory(name="broader", label="broader term")
        pt4 = PropertyTypeFactory(name="narrower", label="narrower term")
        RelationFactory(property_type=pt3, source=self.group, target=supergroup)
        RelationFactory(property_type=pt4, source=supergroup, target=self.group)
        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "some prefLabel")
        self.assertEqual(resp.pyquery('.content p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('.content ul').size(), 3)
        self.assertEqual(resp.pyquery('.listing:eq(1)').size(), 1)
        self.assertEqual(resp.pyquery('.listing:eq(1)').text(),
                         "concept prefLabel")
        self.assertEqual(resp.pyquery('.listing:eq(0)').size(), 1)
        self.assertEqual(resp.pyquery('.listing:eq(0)').text(),
                         "supergroup prefLabel")
        self.assertEqual(resp.pyquery('.content li.clearfix').size(), 1)
        self.assertEqual(resp.pyquery('.content li.clearfix').text(),
                         "English some prefLabel")

    def test_redirect(self):
        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content h5.h5-url').text().split()[-1]
        self.assertTrue(settings.GEMET_URL in url)
        self.assertTrue(url.endswith(self.group.code))

    def test_404_error(self):
        url = reverse('group', kwargs={'code': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())


class TestGroupViewWithUser(GemetTest):
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
        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition p').text(),
                         "definition new")

    def test_relations_pending(self):
        self.supergroup = SuperGroupFactory()
        self.concept = TermFactory()
        PropertyFactory(concept=self.supergroup, value="SuperGroup",
                        status=PUBLISHED)
        PropertyFactory(concept=self.concept, value="Concept",
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="group", label="Group")
        pt2 = PropertyTypeFactory(name="groupMember", label="Concepts")
        pt3 = PropertyTypeFactory(name="broader", label="Broader")
        pt4 = PropertyTypeFactory(name="narrower", label="Narrower")

        RelationFactory(property_type=pt1, source=self.concept,
                        target=self.group, status=PENDING)
        RelationFactory(property_type=pt2, source=self.group,
                        target=self.concept, status=PENDING)
        RelationFactory(property_type=pt3, source=self.group,
                        target=self.supergroup, status=PENDING)
        RelationFactory(property_type=pt4, source=self.supergroup,
                        target=self.group, status=PENDING)

        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        relations_displayed = resp.pyquery('ul.listing').text().split()
        self.assertEqual(len(relations_displayed), 2)
        self.assertEqual(relations_displayed[0], "SuperGroup")
        self.assertEqual(relations_displayed[1], "Concept")

    def test_relations_prefLabel_pending(self):
        self.supergroup = SuperGroupFactory()
        PropertyFactory(concept=self.supergroup, value="SuperGroupOld",
                        status=DELETED_PENDING)
        PropertyFactory(concept=self.supergroup, value="SuperGroupNew",
                        status=PENDING)
        pt1 = PropertyTypeFactory(name="broader", label="Broader")
        pt2 = PropertyTypeFactory(name="narrower", label="Narrower")
        RelationFactory(property_type=pt1, source=self.group,
                        target=self.supergroup, status=PENDING)
        RelationFactory(property_type=pt2, source=self.supergroup,
                        target=self.group, status=PENDING)

        url = reverse('group', kwargs={'code': self.group.code,
                                       'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        relations_displayed = resp.pyquery('ul.listing').text().split()
        self.assertEqual(len(relations_displayed), 1)
        self.assertEqual(relations_displayed[0], "SuperGroupNew")
