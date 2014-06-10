from django.core.urlresolvers import reverse

from .factories import (
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

        resp = self.app.get(reverse('backbone'))

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

        resp = self.app.get(reverse('backbone_rdf'))

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body.count('supergroup/3'), 2)
        self.assertEqual(resp.body.count('group/2'), 3)
        self.assertEqual(resp.body.count('theme/4'), 3)
        self.assertEqual(resp.body.count('concept/1'), 3)
