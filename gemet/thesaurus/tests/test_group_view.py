from django.core.urlresolvers import reverse

from .factories import GroupFactory, PropertyFactory, PropertyTypeFactory
from .factories import RelationFactory, SuperGroupFactory, TermFactory
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
        self.assertEqual(302, self.app.get(url).status_int)

    def test_404_error(self):
        url = reverse('group', kwargs={'code': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
