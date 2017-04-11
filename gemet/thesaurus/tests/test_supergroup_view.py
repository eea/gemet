from django.core.urlresolvers import reverse
from django.conf import settings

from .factories import GroupFactory, LanguageFactory, PropertyFactory
from .factories import PropertyTypeFactory, RelationFactory, SuperGroupFactory
from .factories import UserFactory
from . import GemetTest, ERROR_404
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED


class TestSuperGroupView(GemetTest):
    def setUp(self):
        self.supergroup = SuperGroupFactory()
        PropertyFactory(concept=self.supergroup, name="prefLabel",
                        value="some prefLabel")

    def test_supergroup_no_concept(self):
        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content ul').size(), 1)
        self.assertEqual(resp.pyquery('.content ul').children().size(), 1)
        self.assertEqual(resp.pyquery('.content ul li').text(),
                         "English some prefLabel")

    def test_supergroup_one_group(self):
        group = GroupFactory()
        PropertyFactory(concept=group, name="prefLabel",
                        value="group prefLabel")
        pt1 = PropertyTypeFactory(name="narrower",
                                  label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=group)
        RelationFactory(property_type=pt2, source=group,
                        target=self.supergroup)
        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content ul').size(), 2)
        self.assertEqual(resp.pyquery('.content ul.listing').children().size(),
                         1)
        self.assertEqual(resp.pyquery('.content ul.listing li').text(),
                         "group prefLabel")
        self.assertEqual(
            resp.pyquery('.content ul#translations').children().size(), 1)
        self.assertEqual(resp.pyquery('.content ul#translations li').text(),
                         "English some prefLabel")

    def test_supergroup_two_groups(self):
        group1 = GroupFactory(code="1")
        PropertyFactory(concept=group1, name="prefLabel",
                        value="group1 prefLabel")
        pt1 = PropertyTypeFactory(name="narrower",
                                  label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=group1)
        RelationFactory(property_type=pt2, source=group1,
                        target=self.supergroup)
        group2 = GroupFactory(code="2")
        PropertyFactory(concept=group2, name="prefLabel",
                        value="group2 prefLabel")
        pt3 = PropertyTypeFactory(name="narrower",
                                  label="narrower term")
        pt4 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt3, source=self.supergroup,
                        target=group2)
        RelationFactory(property_type=pt4, source=group2,
                        target=self.supergroup)
        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('#prefLabel').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('p.alert:eq(0)').text(),
                         "Definition is not available.")
        self.assertEqual(resp.pyquery('p.alert:eq(1)').text(),
                         "Scope note is not available.")
        self.assertEqual(resp.pyquery('.content ul').size(), 2)
        self.assertEqual(
            resp.pyquery('.content ul.listing').children().size(), 2)
        self.assertEqual(resp.pyquery('.content ul.listing li:eq(0)').text(),
                         "group1 prefLabel")
        self.assertEqual(resp.pyquery('.content ul.listing li:eq(1)').text(),
                         "group2 prefLabel")
        self.assertEqual(
            resp.pyquery('.content ul#translations').children().size(), 1)
        self.assertEqual(
            resp.pyquery('.content ul#translations').children().text(),
            "English some prefLabel")

    def test_redirect(self):
        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url)
        url = resp.pyquery('.content h5.h5-url').text().split()[-1]
        self.assertTrue(settings.GEMET_URL in url)
        self.assertTrue(url.endswith(self.supergroup.code))

    def test_404_error(self):
        url = reverse('supergroup', kwargs={'code': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())


class TestSuperGroupViewWithUser(GemetTest):
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
                        value="scopenote", status=DELETED_PENDING)
        PropertyFactory(concept=self.supergroup, name="scopeNote",
                        value="scopeNote new", status=PENDING)

        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('.content #prefLabel').text(),
                         "prefLabel new")
        self.assertEqual(resp.pyquery('.content #definition-text').text(),
                         "definition new")
        self.assertEqual(resp.pyquery('.content #scope-note').text(),
                         "scopeNote new")

    def test_relations_pending(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, value="Group",
                        status=PUBLISHED)
        pt1 = PropertyTypeFactory(name="narrower", label="Narrower")
        pt2 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=self.group, status=PENDING)
        RelationFactory(property_type=pt2, source=self.group,
                        target=self.supergroup, status=PENDING)

        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        relations_displayed = resp.pyquery('.content ul.listing').text().split()
        self.assertEqual(len(relations_displayed), 1)
        self.assertEqual(relations_displayed[0], "Group")

    def test_relations_prefLabel_pending(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, value="OldGroup",
                        status=DELETED_PENDING)
        PropertyFactory(concept=self.group, value="NewGroup",
                        status=PENDING)
        pt1 = PropertyTypeFactory(name="narrower", label="Narrower")
        pt2 = PropertyTypeFactory(name="broader", label="Broader")
        RelationFactory(property_type=pt1, source=self.supergroup,
                        target=self.group, status=PENDING)
        RelationFactory(property_type=pt2, source=self.group,
                        target=self.supergroup, status=PENDING)

        url = reverse('supergroup', kwargs={'code': self.supergroup.code,
                                            'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        relations_displayed = resp.pyquery('.content ul.listing').text().split()
        self.assertEqual(len(relations_displayed), 1)
        self.assertEqual(relations_displayed[0], "NewGroup")
