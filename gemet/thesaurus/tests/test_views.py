import pyquery

from django_webtest import WebTest
from django.core.urlresolvers import reverse

from .factories import (
    ConceptFactory,
    PropertyFactory,
    LanguageFactory,
    NamespaceFactory,
    RelationFactory,
    PropertyTypeFactory,
)


class TestThemesView(WebTest):
    def test_no_theme(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('.themes li').length, 0)

    def test_one_theme(self):
        theme = ConceptFactory()
        PropertyFactory(concept=theme)

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 1)

        self.assertEqual(resp.pyquery('.themes li a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        self.assertEqual(resp.pyquery('.themes li a').text(),
                         u'administration')

    def test_contains_more_themes(self):
        theme1 = ConceptFactory(id=1, code="1")
        PropertyFactory(concept=theme1, value="Theme 1")
        theme2 = ConceptFactory(id=2, code="2")
        PropertyFactory(concept=theme2, value="Theme 2")

        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.themes li').length, 2)

        self.assertEqual(resp.pyquery('.themes li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(0) a').text(),
                         u'Theme 1'
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').text(),
                         u'Theme 2'
                         )


class TestThemeConceptsView(WebTest):
    def setUp(self):
        self.ns_concept = NamespaceFactory(id=2, heading="Concepts")
        self.theme = ConceptFactory()

        PropertyFactory(concept=self.theme)
        self.pt1 = PropertyTypeFactory(id=1, name="themeMember",
                                       label="Theme member")
        self.pt2 = PropertyTypeFactory(id=2, name="theme", label="Theme")

    def test_one_theme_concept(self):
        concept = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept, value="Concept value")

        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept)
        RelationFactory(property_type=self.pt2, source=concept,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.concepts li').length, 1)

        """
        after TO_DO list

        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 1}))
                         )
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept value')

    def test_more_theme_concepts(self):
        concept1 = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept1, value="Concept 1")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept1)
        RelationFactory(property_type=self.pt2, source=concept1,
                        target=self.theme)

        concept2 = ConceptFactory(id=3, code="3", namespace=self.ns_concept)
        PropertyFactory(concept=concept2, value="Concept 2")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        #after TO_DO list. An a href needed
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'Concept 1')

        #after TO_DO list. An a href needed
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(1) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """

        self.assertEqual(resp.pyquery('.concepts li:eq(1)').text(),
                         u'Concept 2')

    def test_letter_selected(self):
        concept2 = ConceptFactory(id=2, code="2", namespace=self.ns_concept)
        PropertyFactory(concept=concept2, value="A_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept2)
        RelationFactory(property_type=self.pt2, source=concept2,
                        target=self.theme)

        concept3 = ConceptFactory(id=3, code="3", namespace=self.ns_concept)
        PropertyFactory(concept=concept3, value="B_CONCEPT")
        RelationFactory(property_type=self.pt1, source=self.theme,
                        target=concept3)
        RelationFactory(property_type=self.pt2, source=concept3,
                        target=self.theme)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})

        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=1))
        self.assertEqual(200, resp.status_int)
        for concept_index in range(0, len(resp.pyquery('.concepts li'))):
            self.assertEqual(resp.pyquery('.concepts li:eq({0})'
                                          .format(concept_index)).text()[0],
                             'A')

        resp = self.app.get('{_url}?letter={letter}'
                            .format(_url=url, letter=2))
        self.assertEqual(200, resp.status_int)
        for concept_index in range(0, len(resp.pyquery('.concepts li'))):
            self.assertEqual(resp.pyquery('.concepts li:eq({0})'
                                          .format(concept_index)).text()[0],
                             'B')


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
