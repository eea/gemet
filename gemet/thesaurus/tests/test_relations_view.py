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


class TestRelationsView(WebTest):
    def setUp(self):
        self.ns_group = NamespaceFactory(id=3, heading="Groups")
        self.group = ConceptFactory(namespace=self.ns_group)
        PropertyFactory(concept=self.group, value="Group")

    def test_group_with_no_member(self):
        url = reverse('relations', kwargs={'group_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'Group')
        self.assertEqual(resp.pyquery('.groupMembers > li').length, 0)

    def test_group_with_one_member(self):
        ns_concept = NamespaceFactory(id=1, heading="Concept")
        concept = ConceptFactory(id=2, code="2", namespace=ns_concept)
        PropertyFactory(concept=concept, value="Concept")

        pt1=PropertyTypeFactory(id=1, name="groupMember", label="Group member")
        pt2=PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        url = reverse('relations', kwargs={'group_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'Group')
        self.assertEqual(resp.pyquery('.groupMembers > li').length, 1)
        self.assertEqual(resp.pyquery('.groupMembers > li a:eq(0)')
                         .attr('href'),
                         u'{url}?exp=2'.format(
                             url=reverse('relations', kwargs={'langcode': 'en',
                                                              'group_id': 1}))
                         )
        self.assertEqual(resp.pyquery('.groupMembers > li a:eq(0)').text(),
                         "+")
        self.assertEqual(resp.pyquery('.groupMembers > li a:eq(1)')
                         .attr('href'),
                         u'{url}'.format(url=reverse('concept',
                                                     kwargs={'langcode': 'en',
                                                             'concept_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.groupMembers > li a:eq(1)').text(),
                         "Concept")
