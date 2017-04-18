import unittest

from django.core.urlresolvers import reverse

from .factories import (
    LanguageFactory,
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    ThemeFactory,
    GroupFactory,
    SuperGroupFactory,
    ForeignRelationFactory,
)
from . import GemetTest


class TestExports(GemetTest):

    @unittest.skip('Exports are now saved to static files')
    def test_themes_groups_relations_html(self):
        term1 = TermFactory(code='11')
        term2 = TermFactory(code='12')
        term3 = TermFactory(code='13')
        theme = ThemeFactory(code='21')
        group = GroupFactory(code='31')

        p11 = PropertyTypeFactory()
        p12 = PropertyTypeFactory(name='theme', label='Theme')
        p21 = PropertyTypeFactory(name='groupMember', label='Group member')
        p22 = PropertyTypeFactory(name='group', label='Group')

        RelationFactory(property_type=p11, source=theme, target=term1)
        RelationFactory(property_type=p12, source=term1, target=theme)
        RelationFactory(property_type=p21, source=group, target=term2)
        RelationFactory(property_type=p22, source=term2, target=group)
        RelationFactory(property_type=p11, source=theme, target=term3)
        RelationFactory(property_type=p12, source=term3, target=theme)
        RelationFactory(property_type=p21, source=group, target=term3)
        RelationFactory(property_type=p22, source=term3, target=group)

        rows = ['11 Theme 21', '13 Theme 21', '12 Group 31', '13 Group 31']

        resp = self.app.get(reverse('gemet-backbone.html'))

        self.assertEqual(resp.status_int, 200)
        for i in range(0, 4):
            self.assertTrue(
                resp.pyquery('tbody tr:eq(%s)' % (str(i))).text() in rows
            )

    @unittest.skip('Exports are now saved to static files')
    def test_themes_groups_relations_rdf(self):
        term = TermFactory()
        theme = ThemeFactory()
        group = GroupFactory()
        supergroup = SuperGroupFactory()

        p11 = PropertyTypeFactory()
        p12 = PropertyTypeFactory(name='theme', label='Theme')
        p21 = PropertyTypeFactory(name='groupMember', label='Group member')
        p22 = PropertyTypeFactory(name='group', label='Group')
        p13 = PropertyTypeFactory(name='broader', label='Broader')

        RelationFactory(property_type=p11, source=theme, target=term)
        RelationFactory(property_type=p12, source=term, target=theme)
        RelationFactory(property_type=p21, source=group, target=term)
        RelationFactory(property_type=p22, source=term, target=group)
        RelationFactory(property_type=p13, source=group, target=supergroup)

        resp = self.app.get(reverse('gemet-backbone.rdf'))

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, 'text/xml')
        self.assertEqual(resp.content.count('supergroup/3'), 3)
        self.assertEqual(resp.content.count('group/2'), 4)
        self.assertEqual(resp.content.count('theme/4'), 3)
        self.assertEqual(resp.content.count('concept/1'), 3)

    @unittest.skip('Exports are now saved to static files')
    def test_label_and_definitions_html(self):
        term1 = TermFactory(code='1')
        term2 = TermFactory(code='2')
        term3 = TermFactory(code='3')
        term4 = TermFactory(code='4')
        spanish_term = TermFactory(code='5')
        spanish = LanguageFactory(code='es', name='Spanish')

        PropertyFactory(concept=term1, name='prefLabel', value='A')

        PropertyFactory(concept=term2, name='prefLabel', value='A')
        PropertyFactory(concept=term2, name='definition', value='B')

        PropertyFactory(concept=term3, name='prefLabel', value='A')
        PropertyFactory(concept=term3, name='definition', value='B')
        PropertyFactory(concept=term3, name='scopeNote', value='C')

        PropertyFactory(concept=term4, name='prefLabel', value='A')
        PropertyFactory(concept=term4, name='definition', value='B')
        PropertyFactory(concept=term4, name='scopeNote', value='C')
        PropertyFactory(concept=term4, name='notation', value='D')

        PropertyFactory(concept=spanish_term, language=spanish,
                        name='prefLabel', value='X')

        resp = self.app.get(reverse('gemet-definitions.html'))

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.pyquery('tbody tr').size(), 4)

        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(0)').text(), '1')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(1)').text(), 'A')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(2)').text(), '')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(3)').text(), '')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(4)').text(), '')

        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(0)').text(), '2')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(1)').text(), 'A')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(2)').text(), 'B')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(3)').text(), '')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(4)').text(), '')

        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(0)').text(), '3')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(1)').text(), 'A')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(2)').text(), 'B')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(3)').text(), 'C')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(4)').text(), '')

        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(0)').text(), '4')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(1)').text(), 'A')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(2)').text(), 'B')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(3)').text(), 'C')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(4)').text(), 'D')

    @unittest.skip('Exports are now saved to static files')
    def test_gemet_groups_html(self):
        supergroup = SuperGroupFactory(code='10')
        group = GroupFactory(code='11')
        theme = ThemeFactory(code='12')

        PropertyFactory(concept=supergroup, name='prefLabel', value='A')
        PropertyFactory(concept=group, name='prefLabel', value='B')
        PropertyFactory(concept=theme, name='prefLabel', value='C')

        p1 = PropertyTypeFactory(name='narrower', label='narrower term')
        p2 = PropertyTypeFactory(name='broader', label='broader term')
        RelationFactory(property_type=p1, source=supergroup, target=group)
        RelationFactory(property_type=p2, source=group, target=supergroup)

        resp = self.app.get(reverse('gemet-groups.html'))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('table:eq(0) tbody tr').size(), 1)
        self.assertEqual(resp.pyquery('table:eq(0) tbody td:eq(0)').text(),
                         '10')
        self.assertEqual(resp.pyquery('table:eq(0) tbody td:eq(1)').text(),
                         'SuperGroup')
        self.assertEqual(resp.pyquery('table:eq(0) tbody td:eq(2)').text(), '')
        self.assertEqual(resp.pyquery('table:eq(0) tbody td:eq(3)').text(),
                         'A')
        self.assertEqual(resp.pyquery('table:eq(1) tbody tr').size(), 1)
        self.assertEqual(resp.pyquery('table:eq(1) tbody td:eq(0)').text(),
                         '11')
        self.assertEqual(resp.pyquery('table:eq(1) tbody td:eq(1)').text(),
                         'Group')
        self.assertEqual(resp.pyquery('table:eq(1) tbody td:eq(2)').text(),
                         '10')
        self.assertEqual(resp.pyquery('table:eq(1) tbody td:eq(3)').text(),
                         'B')
        self.assertEqual(resp.pyquery('table:eq(2) tbody tr').size(), 1)
        self.assertEqual(resp.pyquery('table:eq(2) tbody td:eq(0)').text(),
                         '12')
        self.assertEqual(resp.pyquery('table:eq(2) tbody td:eq(1)').text(),
                         'Theme')
        self.assertEqual(resp.pyquery('table:eq(2) tbody td:eq(2)').text(),
                         'C')

    @unittest.skip('Exports are now saved to static files')
    def test_gemet_relations_html(self):
        term1 = TermFactory(code='11')
        term2 = TermFactory(code='12')
        term3 = TermFactory(code='13')

        p1 = PropertyTypeFactory(name='narrower', label='narrower term')
        p2 = PropertyTypeFactory(name='broader', label='broader term')
        p3 = PropertyTypeFactory(name='related', label='related')
        p4 = PropertyTypeFactory(name='exactMatch', label='exact match')
        p5 = PropertyTypeFactory(name='closeMatch', label='close match')
        RelationFactory(property_type=p1, source=term1, target=term2)
        RelationFactory(property_type=p2, source=term2, target=term1)
        RelationFactory(property_type=p3, source=term2, target=term3)
        RelationFactory(property_type=p3, source=term3, target=term2)
        ForeignRelationFactory(concept=term1, uri='concept_uri1',
                               property_type=p4)
        ForeignRelationFactory(concept=term1, uri='concept_uri2',
                               property_type=p5)
        ForeignRelationFactory(concept=term2, uri='concept_uri3',
                               property_type=p4)
        rows = ['11 Narrower 12', '11 Exactmatch concept_uri1',
                '11 Closematch concept_uri2', '12 Broader 11', '12 Related 13',
                '12 Closematch concept_uri3', '13 Related 12']

        resp = self.app.get(reverse('gemet-relations.html'))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.pyquery('table').size(), 1)
        self.assertEqual(resp.pyquery('tbody tr').size(), 7)
        for i in range(0, 4):
            self.assertTrue(
                resp.pyquery('tbody tr:eq(%s)' % (str(i))).text() in rows
            )

    @unittest.skip('Exports are now saved to static files')
    def test_skoscore(self):
        term1 = TermFactory(code='11')
        term2 = TermFactory(code='12')
        term3 = TermFactory(code='13')

        p1 = PropertyTypeFactory(name='narrower', label='narrower term')
        p2 = PropertyTypeFactory(name='broader', label='broader term')
        p3 = PropertyTypeFactory(name='related', label='related')
        p4 = PropertyTypeFactory(name='exactMatch', label='exact match')
        p5 = PropertyTypeFactory(name='closeMatch', label='close match')
        RelationFactory(property_type=p1, source=term1, target=term2)
        RelationFactory(property_type=p2, source=term2, target=term1)
        RelationFactory(property_type=p3, source=term2, target=term3)
        RelationFactory(property_type=p3, source=term3, target=term2)
        ForeignRelationFactory(concept=term1, uri='concept_uri1',
                               property_type=p4)
        ForeignRelationFactory(concept=term1, uri='concept_uri2',
                               property_type=p5)
        ForeignRelationFactory(concept=term2, uri='concept_uri3',
                               property_type=p4)

        resp = self.app.get(reverse('gemet-skoscore.rdf'))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.content_type, 'text/xml')
        self.assertEqual(resp.content.count('concept/11'), 2)
        self.assertEqual(resp.content.count('concept/12'), 3)
        self.assertEqual(resp.content.count('concept/13'), 2)
        self.assertEqual(resp.content.count('broader'), 1)
        self.assertEqual(resp.content.count('narrower'), 1)
        self.assertEqual(resp.content.count('related'), 2)
        self.assertEqual(resp.content.count('exactMatch'), 2)
        self.assertEqual(resp.content.count('closeMatch'), 1)
        self.assertEqual(resp.content.count('concept_uri1'), 1)
        self.assertEqual(resp.content.count('concept_uri2'), 1)
        self.assertEqual(resp.content.count('concept_uri3'), 1)

    @unittest.skip('Exports are now saved to static files')
    def test_label_and_definitions_rdf(self):
        term1 = TermFactory(code='11')
        term2 = TermFactory(code='12')

        PropertyFactory(concept=term1, name='prefLabel', value='A_label')
        PropertyFactory(concept=term2, name='prefLabel', value='B_label')
        PropertyFactory(concept=term2, name='definition',
                        value='B_definition')

        spanish = LanguageFactory(code='es', name='Spanish')
        term3 = TermFactory(code='13')
        PropertyFactory(concept=term3, language=spanish, name='prefLabel',
                        value='C_label')
        PropertyFactory(concept=term3, language=spanish, name='definition',
                        value='C_definition')

        resp = self.app.get(reverse('gemet-definitions.rdf', args=['en']))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.content_type, 'text/xml')
        self.assertEqual(resp.content.count('xml:lang="en"'), 1)
        self.assertEqual(resp.content.count('concept/11'), 1)
        self.assertEqual(resp.content.count('A_label'), 1)
        self.assertEqual(resp.content.count('concept/12'), 1)
        self.assertEqual(resp.content.count('B_label'), 1)
        self.assertEqual(resp.content.count('B_definition'), 1)
        self.assertEqual(resp.content.count('concept/13'), 0)
        self.assertEqual(resp.content.count('C_label'), 0)
        self.assertEqual(resp.content.count('C_definition'), 0)

    @unittest.skip('Exports are now saved to static files')
    def test_gemet_groups_rdf(self):
        supergroup = SuperGroupFactory(code='10')
        group = GroupFactory(code='11')
        theme = ThemeFactory(code='12')
        PropertyFactory(concept=supergroup, name='prefLabel', value='A_label')
        PropertyFactory(concept=group, name='prefLabel', value='B_label')
        PropertyFactory(concept=theme, name='prefLabel', value='C_label')

        spanish = LanguageFactory(code='es', name='Spanish')
        es_supergroup = SuperGroupFactory(code='20')
        es_group = GroupFactory(code='21')
        es_theme = ThemeFactory(code='22')
        PropertyFactory(concept=es_supergroup, language=spanish,
                        name='prefLabel', value='A_label_spanish')
        PropertyFactory(concept=es_group, language=spanish, name='prefLabel',
                        value='B_label_spanish')
        PropertyFactory(concept=es_theme, language=spanish, name='prefLabel',
                        value='C_label_spanish')

        resp = self.app.get(reverse('gemet-groups.rdf', args=['en']))

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.content_type, 'text/xml')
        self.assertEqual(resp.content.count('xml:lang="en"'), 1)
        self.assertEqual(resp.content.count('supergroup/10'), 1)
        self.assertEqual(resp.content.count('A_label'), 1)
        self.assertEqual(resp.content.count('group/11'), 1)
        self.assertEqual(resp.content.count('B_label'), 1)
        self.assertEqual(resp.content.count('theme/12'), 1)
        self.assertEqual(resp.content.count('C_label'), 1)
        self.assertEqual(resp.content.count('A_label_spanish'), 0)
        self.assertEqual(resp.content.count('supergroup/20'), 0)
        self.assertEqual(resp.content.count('B_label_spanish'), 0)
        self.assertEqual(resp.content.count('group/21'), 0)
        self.assertEqual(resp.content.count('C_label_spanish'), 0)
        self.assertEqual(resp.content.count('theme/22'), 0)
