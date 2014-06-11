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
)
from . import GemetTest

class TestExports(GemetTest):

    def test_themes_groups_relations_html(self):
        term1 = TermFactory(id='11', code='11')
        term2 = TermFactory(id='12', code='12')
        term3 = TermFactory(id='13', code='13')
        theme = ThemeFactory(id='21', code='21')
        group = GroupFactory(id='31', code='31')

        p11 = PropertyTypeFactory()
        p12 = PropertyTypeFactory(id='2', name='theme', label='Theme')
        p21 = PropertyTypeFactory(id='3', name='groupMember',
                                  label='Group member')
        p22 = PropertyTypeFactory(id='4', name='group', label='Group')

        r11 = RelationFactory(property_type=p11, source=theme, target=term1)
        r12 = RelationFactory(property_type=p12, source=term1, target=theme)
        r21 = RelationFactory(property_type=p21, source=group, target=term2)
        r22 = RelationFactory(property_type=p22, source=term2, target=group)
        r31 = RelationFactory(property_type=p11, source=theme, target=term3)
        r32 = RelationFactory(property_type=p12, source=term3, target=theme)
        r41 = RelationFactory(property_type=p21, source=group, target=term3)
        r42 = RelationFactory(property_type=p22, source=term3, target=group)

        resp = self.app.get(reverse('gemet-backbone.html'))

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(0)').text(), '11')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(1)').text(),
                         'Theme')
        self.assertEqual(resp.pyquery('table tr:eq(0) td:eq(2)').text(), '21')

        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(0)').text(), '13')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(1)').text(),
                         'Theme')
        self.assertEqual(resp.pyquery('table tr:eq(1) td:eq(2)').text(), '21')

        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(0)').text(), '12')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(1)').text(),
                         'Group')
        self.assertEqual(resp.pyquery('table tr:eq(2) td:eq(2)').text(), '31')

        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(0)').text(), '13')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(1)').text(),
                         'Group')
        self.assertEqual(resp.pyquery('table tr:eq(3) td:eq(2)').text(), '31')

    def test_themes_groups_relations_rdf(self):
        term = TermFactory()
        theme = ThemeFactory()
        group = GroupFactory()
        supergroup = SuperGroupFactory()

        p11 = PropertyTypeFactory()
        p12 = PropertyTypeFactory(id='2', name='theme', label='Theme')
        p21 = PropertyTypeFactory(id='3', name='groupMember',
                                  label='Group member')
        p22 = PropertyTypeFactory(id='4', name='group', label='Group')

        r11 = RelationFactory(property_type=p11, source=theme, target=term)
        r12 = RelationFactory(property_type=p12, source=term, target=theme)
        r21 = RelationFactory(property_type=p21, source=group, target=term)
        r22 = RelationFactory(property_type=p22, source=term, target=group)

        resp = self.app.get(reverse('gemet-backbone.rdf'))

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.count('supergroup/3'), 2)
        self.assertEqual(resp.body.count('group/2'), 3)
        self.assertEqual(resp.body.count('theme/4'), 3)
        self.assertEqual(resp.body.count('concept/1'), 3)

    def test_label_and_definitions(self):
        term1 = TermFactory(id='1', code='1')
        term2 = TermFactory(id='2', code='2')
        term3 = TermFactory(id='3', code='3')
        term4 = TermFactory(id='4', code='4')
        spanish_term = TermFactory(id='5', code='5')
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
