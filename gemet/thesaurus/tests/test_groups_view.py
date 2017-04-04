from django.core.urlresolvers import reverse

from .factories import (
    GroupFactory,
    LanguageFactory,
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    SuperGroupFactory,
    UserFactory
)
from . import GemetTest
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED


class TestGroupsView(GemetTest):
    # Actually, this tests the HierarchicalListings link

    def setUp(self):
        self.supergroup = SuperGroupFactory()
        self.supergroup_name = PropertyFactory(concept=self.supergroup,
                                               value="Super Group")

    def test_one_supergroup_no_group(self):
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content h3').text(), 'Super Group')
        self.assertEqual(resp.pyquery('.content .groups li').size(), 0)

    def test_one_supergroup_one_group(self):
        group = GroupFactory()
        PropertyFactory(concept=group, value="Group")

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup, target=group)
        RelationFactory(property_type=pt2, source=group, target=self.supergroup)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content .listing.no-list > li').size(),
                         1)
        self.assertEqual(resp.pyquery('.content .listing.no-list h3').text(),
                         'Super Group')
        self.assertEqual(resp.pyquery('.content .groups li').size(), 1)
        self.assertEqual(resp.pyquery('.content .groups li a').attr('href'),
                         reverse('relations', kwargs={'langcode': 'en',
                                                      'group_code': group.code})
                         )
        self.assertEqual(resp.pyquery('.content .groups li a').text(), 'Group')

    def test_more_supergroups_no_group(self):
        supergroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=supergroup, value="Super Group 2")

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content .listing.no-list > li').size(),
                         2)
        self.assertEqual(resp.pyquery('.content .groups li').size(), 0)
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(0) h3').text(),
            'Super Group'
        )
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(1) h3').text(),
            'Super Group 2'
        )

    def test_more_supergroups_one_group(self):
        supergroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=supergroup, value="Super Group 2")

        group = GroupFactory()
        PropertyFactory(concept=group, value="Group")

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup, target=group)
        RelationFactory(property_type=pt2, source=group, target=self.supergroup)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['language'].code, 'en')
        self.assertEqual(resp.pyquery('.content .listing.no-list > li').size(),
                         2)
        self.assertEqual(resp.pyquery('.content .groups li').size(), 1)
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(0) h3').text(),
            'Super Group'
        )
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(1) h3').text(),
            'Super Group 2'
        )
        self.assertEqual(resp.pyquery('.content .groups li:eq(0)').text(),
                         'Group')
        self.assertEqual(
            resp.pyquery('.content .groups li:eq(0) a').attr('href'),
            reverse('relations', kwargs={'langcode': 'en',
                                         'group_code': group.code})
        )
        self.assertEqual(resp.pyquery('.content .groups li:eq(1)').text(), '')


class TestGroupsViewWithUser(GemetTest):
    def setUp(self):
        self.supergroup = SuperGroupFactory()
        self.supergroup_name = PropertyFactory(concept=self.supergroup,
                                               value="Super Group",
                                               status=PUBLISHED)
        user = UserFactory()
        LanguageFactory()
        self.user = user.username

    def test_supergroup_name_pending(self):
        self.supergroup_name.status = DELETED_PENDING
        self.supergroup_name.save()
        PropertyFactory(concept=self.supergroup,
                        value="Super Group New",
                        status=PENDING)
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').size(), 1)
        self.assertEqual(resp.pyquery('.content h3').text(), 'Super Group New')

    def test_supergroup_group_relation_pending(self):
        supergroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=supergroup,
                        value="Super Group 2",
                        status=PUBLISHED)
        group = GroupFactory()
        PropertyFactory(concept=group,
                        value="Group",
                        status=PUBLISHED)

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup, target=group,
                        status=PENDING)
        RelationFactory(property_type=pt2, source=group, target=self.supergroup,
                        status=PENDING)
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content .listing.no-list > li').size(),
                         2)
        self.assertEqual(resp.pyquery('.content .groups li').size(), 1)
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(0) h3').text(),
            'Super Group'
        )
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(1) h3').text(),
            'Super Group 2'
        )
        self.assertEqual(resp.pyquery('.content .groups li:eq(0)').text(),
                         'Group')
        self.assertEqual(
            resp.pyquery('.content .groups li:eq(0) a').attr('href'),
            reverse('relations', kwargs={'langcode': 'en',
                                         'group_code': group.code})
        )

    def test_new_supergroup(self):
        supergroup = SuperGroupFactory(status=PENDING)
        PropertyFactory(concept=supergroup,
                        value="New Super Group",
                        status=PENDING)
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(
            resp.pyquery('.content .listing.no-list li:eq(0) h3').text(),
            'New Super Group'
        )

    def test_group_name_pending(self):
        supergroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=supergroup,
                        value="Super Group 2",
                        status=PUBLISHED)
        group = GroupFactory()
        PropertyFactory(concept=group,
                        value="Group",
                        status=PENDING)

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup, target=group,
                        status=PENDING)
        RelationFactory(property_type=pt2, source=group, target=self.supergroup,
                        status=PENDING)
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content .groups li:eq(0)').text(),
                         'Group')

    def test_new_group_pending(self):
        supergroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=supergroup,
                        value="Super Group 2",
                        status=PUBLISHED)
        group = GroupFactory(status=PENDING)
        PropertyFactory(concept=group,
                        value="Group",
                        status=PENDING)

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.supergroup, target=group,
                        status=PENDING)
        RelationFactory(property_type=pt2, source=group, target=self.supergroup,
                        status=PENDING)
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url, user=self.user)
        self.assertEqual(resp.pyquery('.content .groups li:eq(0)').text(),
                         'Group')