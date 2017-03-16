from django.core.urlresolvers import reverse

from .factories import GroupFactory, PropertyFactory, PropertyTypeFactory
from .factories import RelationFactory, SuperGroupFactory
from . import GemetTest, ERROR_404


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
        self.assertEqual(302, self.app.get(url).status_int)

    def test_404_error(self):
        url = reverse('supergroup', kwargs={'code': 1, 'langcode': 'en'})
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery('.error404 h1').text())
