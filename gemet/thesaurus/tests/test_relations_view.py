from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    GroupFactory,
)
from . import GemetTest, ERROR_404
from gemet.thesaurus.utils import exp_encrypt


class TestRelationsView(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, value="Group")

    def test_group_with_no_member(self):
        url = reverse('relations', kwargs={'group_id': self.group.id,
                                           'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'Group')
        self.assertEqual(resp.pyquery('ul:eq(1) > li').size(), 0)

    def test_group_with_one_member(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        url = reverse('relations', kwargs={'group_id': self.group.id,
                                           'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'Group')
        self.assertEqual(resp.pyquery('ul:eq(1) > li').size(), 1)
        self.assertEqual(resp.pyquery('ul:eq(1) > li a:eq(0)').attr('href'),
                         u'{url}?exp={exp}'.
                         format(url=reverse('relations',
                                            kwargs={
                                                'langcode': 'en',
                                                'group_id': self.group.id,
                                            }),
                                exp=exp_encrypt(str(concept.id))
                                )
                         )
        self.assertEqual(resp.pyquery('ul:eq(1) > li a:eq(0)').text(), '+')
        self.assertEqual(resp.pyquery('ul:eq(1) > li a:eq(1)').attr('href'),
                         reverse('concept',
                                 kwargs={'langcode': 'en',
                                         'concept_id': concept.id}))
        self.assertEqual(resp.pyquery('ul:eq(1) > li a:eq(1)').text(),
                         "Concept")

    def test_404_error(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        url = reverse('relations', kwargs={'group_id': concept.id,
                                           'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404').text())
