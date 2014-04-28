import pyquery

from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestGroupsView(WebTest):
    ### Actually, this tests the HierarchicalListings link

    def setUp(self):
        self.ns_superGroup = NamespaceFactory(id=2, heading="Super groups")
        self.superGroup = ConceptFactory(namespace=self.ns_superGroup)
        PropertyFactory(concept=self.superGroup, value="Super Group")

    def test_one_supergroup_no_group(self):
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups li').length, 1)
        self.assertEqual(resp.pyquery('.groups li').length, 0)
        self.assertEqual(resp.pyquery('.supergroups h2').text(),
                         'Super Group')

    def test_one_supergroup_one_group(self):
        ns_group = NamespaceFactory(id=3, heading="Groups")
        group = ConceptFactory(id=2, code="2", namespace=ns_group)
        PropertyFactory(concept=group, value="Group")

        pt1 = PropertyTypeFactory(id=1, name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(id=2, name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.superGroup,
                        target=group)
        RelationFactory(property_type=pt2, source=group,
                        target=self.superGroup)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups > li').length, 1)
        self.assertEqual(resp.pyquery('.groups li').length, 1)
        self.assertEqual(resp.pyquery('.supergroups h2').text(), 'Super Group')
        self.assertEqual(resp.pyquery('.groups li a').attr('href'),
                         u'{url}'.format(url=reverse('relations',
                                                     kwargs={'langcode': 'en',
                                                             'group_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.groups li a').text(), 'Group')

    def test_more_supergroups_no_group(self):
        superGroup = ConceptFactory(id=2, code="2",
                                    namespace=self.ns_superGroup)
        PropertyFactory(concept=superGroup, value="Super Group 2")

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups li').length, 2)
        self.assertEqual(resp.pyquery('.groups li').length, 0)
        self.assertEqual(resp.pyquery('.supergroups li:eq(0) h2').text(),
                         'Super Group')
        self.assertEqual(resp.pyquery('.supergroups li:eq(1) h2').text(),
                         'Super Group 2')

    def test_more_supergroups_one_group(self):
        superGroup = ConceptFactory(id=2, code="2",
                                    namespace=self.ns_superGroup)
        PropertyFactory(concept=superGroup, value="Super Group 2")

        ns_group = NamespaceFactory(id=3, heading="Groups")
        group = ConceptFactory(id=3, code="3", namespace=ns_group)
        PropertyFactory(concept=group, value="Group")

        pt1 = PropertyTypeFactory(id=1, name="narrower", label="narrower term")
        pt2 = PropertyTypeFactory(id=2, name="broader", label="broader term")
        RelationFactory(property_type=pt1, source=self.superGroup,
                        target=group)
        RelationFactory(property_type=pt2, source=group,
                        target=self.superGroup)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups > li').length, 2)
        self.assertEqual(resp.pyquery('.groups li').length, 1)
        self.assertEqual(resp.pyquery('.supergroups li:eq(0) h2').text(),
                         'Super Group')
        self.assertEqual(resp.pyquery('.supergroups li:eq(1) h2').text(),
                         'Super Group 2')

        self.assertEqual(resp.pyquery('.groups li:eq(0)').text(), 'Group')
        self.assertEqual(resp.pyquery('.groups li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('relations',
                                                     kwargs={'langcode': 'en',
                                                             'group_id': 3}))
                         )
        self.assertEqual(resp.pyquery('.groups li:eq(1)').text(), '')