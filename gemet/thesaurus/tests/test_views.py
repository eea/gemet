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


class TestThemesViewLanguageSelection(WebTest):
    def test_other_than_the_default_english(self):
        LanguageFactory(code='es', name='Spanish')

        url = reverse('themes', kwargs={'langcode': 'es'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'es')


class TestThemesView(WebTest):
    def setUp(self):
        LanguageFactory()
        NamespaceFactory()

    def test_no_theme(self):
        url = reverse('themes', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('.themes li').length, 0)

    def test_one_theme(self):
        ConceptFactory()
        PropertyFactory()

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
        ConceptFactory()
        PropertyFactory()
        ConceptFactory(id=2, code="2", namespace_id=4)
        PropertyFactory(concept_id=2, value="agriculture")

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
                         u'administration'
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').attr('href'),
                         u'{url}'.format(url=reverse('theme_concepts',
                                                     kwargs={'langcode': 'en',
                                                             'theme_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.themes li:eq(1) a').text(),
                         u'agriculture'
                         )


class TestThemeConceptsView(WebTest):
    def setUp(self):
        LanguageFactory()
        NamespaceFactory()
        ConceptFactory()
        PropertyFactory()

    def test_one_theme_concept(self):
        NamespaceFactory(id=1, heading="Concepts")
        ConceptFactory(id=2, code="2", namespace_id=1)
        PropertyFactory(concept_id=2, value="CONCEPT")

        PropertyTypeFactory(id=1, name="themeMember", label="Theme member")
        RelationFactory(property_type_id=1, source_id=1, target_id=2)
        PropertyTypeFactory(id=2, name="theme", label="Theme")
        RelationFactory(property_type_id=2, source_id=2, target_id=1)

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
                         u'CONCEPT')

    def test_more_theme_concepts(self):
        NamespaceFactory(id=1, heading="Concepts")
        PropertyTypeFactory(id=1, name="themeMember", label="Theme member")
        PropertyTypeFactory(id=2, name="theme", label="Theme")

        ConceptFactory(id=2, code="2", namespace_id=1)
        PropertyFactory(concept_id=2,
                        value="access to administrative documents")

        RelationFactory(property_type_id=1, source_id=1, target_id=2)
        RelationFactory(property_type_id=2, source_id=2, target_id=1)

        ConceptFactory(id=3, code="3", namespace_id=1)
        PropertyFactory(concept_id=3, value="access to the sea")
        RelationFactory(property_type_id=1, source_id=1, target_id=3)
        RelationFactory(property_type_id=2, source_id=3, target_id=1)

        url = reverse('theme_concepts',
                      kwargs={'langcode': 'en', 'theme_id': 1})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        """
        after TO_DO list

        self.assertEqual(resp.pyquery('.concepts li:eq(0) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(0)').text(),
                         u'access to administrative documents')

        #after TO_DO list. An a href needed
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(1) a').attr('href'),
                         u'{url}'
                         .format(url=reverse('theme_concepts',
                                             kwargs={'langcode': 'en',
                                                     'theme_id': 1}))
                         )
        """
        #invalid test for the moment. The entry goes on the second page.
        """
        self.assertEqual(resp.pyquery('.concepts li:eq(1)').text(),
                         u'access to the sea')
        """

    def test_letter_selected(self):
        NamespaceFactory(id=1, heading="Concepts")
        PropertyTypeFactory(id=1, name="themeMember", label="Theme member")
        PropertyTypeFactory(id=2, name="theme", label="Theme")

        ConceptFactory(id=2, code="2", namespace_id=1)
        PropertyFactory(concept_id=2, value="A_CONCEPT")
        RelationFactory(property_type_id=1, source_id=1, target_id=2)
        RelationFactory(property_type_id=2, source_id=2, target_id=1)

        ConceptFactory(id=3, code="3", namespace_id=1)
        PropertyFactory(concept_id=3, value="B_CONCEPT")
        RelationFactory(property_type_id=1, source_id=1, target_id=3)
        RelationFactory(property_type_id=2, source_id=3, target_id=1)

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
        NamespaceFactory(id=2, heading="Super groups")
        ConceptFactory(namespace_id=2)
        LanguageFactory()
        PropertyFactory(value="SUPER_GROUP")

    def test_one_supergroup_no_group(self):
        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups li').length, 1)
        self.assertEqual(resp.pyquery('.groups li').length, 0)
        self.assertEqual(resp.pyquery('.supergroups h2').text(), 'SUPER_GROUP')

    def test_one_supergroup_one_group(self):
        NamespaceFactory(id=3, heading="Groups")
        ConceptFactory(id=2, code="2", namespace_id=3)
        PropertyFactory(concept_id=2, value="GROUP")

        PropertyTypeFactory(id=1, name="broader", label="broader term")
        RelationFactory(property_type_id=1, source_id=2, target_id=1)
        PropertyTypeFactory(id=2, name="narrower", label="narrower term")
        RelationFactory(property_type_id=2, source_id=1, target_id=2)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups > li').length, 1)
        self.assertEqual(resp.pyquery('.groups li').length, 1)
        self.assertEqual(resp.pyquery('.supergroups h2').text(), 'SUPER_GROUP')
        self.assertEqual(resp.pyquery('.groups li a').attr('href'),
                         u'{url}'.format(url=reverse('relations',
                                                     kwargs={'langcode': 'en',
                                                             'group_id': 2}))
                         )
        self.assertEqual(resp.pyquery('.groups li a').text(), 'GROUP')

    def test_more_supergroups_no_group(self):
        ConceptFactory(id=2, code="2", namespace_id=2)
        PropertyFactory(concept_id=2, value="SUPER_GROUP2")

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups li').length, 2)
        self.assertEqual(resp.pyquery('.groups li').length, 0)
        self.assertEqual(resp.pyquery('.supergroups li:eq(0) h2').text(),
                         'SUPER_GROUP')
        self.assertEqual(resp.pyquery('.supergroups li:eq(1) h2').text(),
                         'SUPER_GROUP2')

    def test_more_supergroups_one_group(self):
        ConceptFactory(id=2, code="2", namespace_id=2)
        PropertyFactory(concept_id=2, value="SUPER_GROUP2")

        NamespaceFactory(id=3, heading="Groups")
        ConceptFactory(id=3, code="3", namespace_id=3)
        PropertyFactory(concept_id=3, value="GROUP")

        PropertyTypeFactory(id=1, name="broader", label="broader term")
        RelationFactory(property_type_id=1, source_id=3, target_id=1)
        PropertyTypeFactory(id=2, name="narrower", label="narrower term")
        RelationFactory(property_type_id=2, source_id=1, target_id=3)

        url = reverse('groups', kwargs={'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
        self.assertEqual(resp.pyquery('.supergroups > li').length, 2)
        self.assertEqual(resp.pyquery('.groups li').length, 1)
        self.assertEqual(resp.pyquery('.supergroups li:eq(0) h2').text(),
                         'SUPER_GROUP')
        self.assertEqual(resp.pyquery('.supergroups li:eq(1) h2').text(),
                         'SUPER_GROUP2')

        self.assertEqual(resp.pyquery('.groups li:eq(0)').text(), 'GROUP')
        self.assertEqual(resp.pyquery('.groups li:eq(0) a').attr('href'),
                         u'{url}'.format(url=reverse('relations',
                                                     kwargs={'langcode': 'en',
                                                             'group_id': 3}))
                         )
        self.assertEqual(resp.pyquery('.groups li:eq(1)').text(), '')


class TestRelationsView(WebTest):
    def setUp(self):
        NamespaceFactory(id=3, heading="Groups")
        ConceptFactory(namespace_id=3)
        LanguageFactory()
        PropertyFactory(value="THIS IS THE GROUP")

    def test_group_with_no_member(self):
        url = reverse('relations', kwargs={'group_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'THIS IS THE GROUP')
        self.assertEqual(resp.pyquery('.groupMembers > li').length, 0)

    def test_group_with_one_member(self):
        NamespaceFactory(id=1, heading="Concept")
        ConceptFactory(id=2, code="2", namespace_id=1)

        PropertyTypeFactory(id=1, name="groupMember", label="Group member")
        RelationFactory(property_type_id=1, source_id=2, target_id=1)
        PropertyTypeFactory(id=2, name="group", label="Group")
        RelationFactory(property_type_id=1, source_id=1, target_id=2)
        PropertyFactory(concept_id=2, value="THIS IS THE CONCEPT")

        url = reverse('relations', kwargs={'group_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')

        self.assertEqual(resp.pyquery('h3').text(), 'THIS IS THE GROUP')
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
                         "THIS IS THE CONCEPT")


class TestConceptView(WebTest):
    def setUp(self):
        NamespaceFactory(id=1, heading="Concept")
        ConceptFactory(namespace_id=1)
        LanguageFactory()
        PropertyFactory()

    def test_ceva(self):
        url = reverse('concept', kwargs={'concept_id': 1, 'langcode': 'en'})
        resp = self.app.get(url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context['langcode'], 'en')
