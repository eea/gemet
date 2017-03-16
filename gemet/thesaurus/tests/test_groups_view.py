from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    GroupFactory,
    SuperGroupFactory,
)
from . import GemetTest


class TestGroupsView(GemetTest):
    # Actually, this tests the HierarchicalListings link

    def setUp(self):
        self.superGroup = SuperGroupFactory()
        PropertyFactory(concept=self.superGroup, value="Super Group")

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
        RelationFactory(property_type=pt1, source=self.superGroup, target=group)
        RelationFactory(property_type=pt2, source=group, target=self.superGroup)

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
        superGroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=superGroup, value="Super Group 2")

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
        superGroup = SuperGroupFactory(code="5")
        PropertyFactory(concept=superGroup, value="Super Group 2")

        group = GroupFactory()
        PropertyFactory(concept=group, value="Group")

        pt1 = PropertyTypeFactory(name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.superGroup, target=group)
        RelationFactory(property_type=pt2, source=group, target=self.superGroup)

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
