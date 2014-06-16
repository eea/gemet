from django.core.urlresolvers import reverse

from .factories import (
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    GroupFactory,
    SuperGroupFactory,
)
from . import GemetTest, ERROR_404


class TestGroupView(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, name="prefLabel",
                        value="some prefLabel")

    def test_group_no_concept(self):
        url = reverse('group', kwargs={'concept_id': self.group.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.infotext:eq(0)').text(),
                         "Definition is not available")
        self.assertEqual(resp.pyquery('.content ul').size(), 1)
        self.assertEqual(resp.pyquery('.content ul').children().size(), 1)
        self.assertEqual(resp.pyquery('.content ul li').text(),
                         "English: some prefLabel")

    def test_group_one_concept_one_supergroup(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, name="prefLabel",
                        value="concept prefLabel")
        pt1 = PropertyTypeFactory(id=1, name="groupMember",
                                  label="Group member")
        pt2 = PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group,
                        target=concept)
        RelationFactory(property_type=pt2, source=concept,
                        target=self.group)

        supergroup = SuperGroupFactory()
        PropertyFactory(concept=supergroup, name="prefLabel",
                        value="supergroup prefLabel")
        pt3 = PropertyTypeFactory(id=3, name="broader", label="broader term")
        pt4 = PropertyTypeFactory(id=4, name="narrower", label="narrower term")
        RelationFactory(property_type=pt3, source=self.group,
                        target=supergroup)
        RelationFactory(property_type=pt4, source=supergroup,
                        target=self.group)
        url = reverse('group', kwargs={'concept_id': self.group.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.content h3').text(), "some prefLabel")
        self.assertEqual(resp.pyquery('.content .infotext:eq(0)').text(),
                         "Definition is not available")
        self.assertEqual(resp.pyquery('.content  ul').size(), 3)
        self.assertEqual(resp.pyquery('.content ul:eq(0)').children().size(),
                         1)
        self.assertEqual(resp.pyquery('.content ul:eq(0) li').text(),
                         "concept prefLabel")
        self.assertEqual(resp.pyquery('.content ul:eq(1)').children().size(),
                         1)
        self.assertEqual(resp.pyquery('.content ul:eq(1) li').text(),
                         "supergroup prefLabel")
        self.assertEqual(resp.pyquery('.content ul:eq(2)').children().size(),
                         1)
        self.assertEqual(resp.pyquery('.content ul:eq(2) li').text(),
                         "English: some prefLabel")

    def test_redirect(self):
        url = reverse('group', kwargs={'concept_id': self.group.id,
                                       'langcode': 'en'})
        resp = self.app.get(url)

        url = resp.pyquery('h4:eq(2)').text().split('<')[1].split('>')[0]
        self.assertEqual(302, self.app.get(url).status_int)

    def test_404_error(self):
        url = reverse('group', kwargs={'concept_id': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404').text())
