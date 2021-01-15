# -*- coding: utf-8 -*-
from django.core.files import File
from django.test import TestCase, Client

from .factories import (
    VersionFactory, TermFactory, GroupFactory, ThemeFactory, Relation
)
from gemet.thesaurus.models import (
    Concept, Term, Group, Theme, Import, Property, PropertyType
)


class ConceptImportView(TestCase):

    # Create namespaces, languages, property types, and users
    fixtures = ['data.json']

    def setUp(self):
        version = VersionFactory(identifier='')
        self.client = Client()

        i = 1
        # Create broader concepts
        for value in ['pollution', 'impact source']:
            concept = TermFactory(code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version
            )
            i += 1

        # Create groups
        for value in ['BIOSPHERE', 'HYDROSPHERE', 'WASTES']:
            concept = GroupFactory(code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version,
            )
            i += 1
        # Make `pollution` a member of `WASTES`
        pollution_concept = Term.objects.get_by_name('pollution')
        wastes_group = Group.objects.get_by_name('WASTES')
        pollution_concept.source_relations.create(
            target=wastes_group,
            version_added=version,
            property_type=PropertyType.objects.get(name='group')
        )
        # Create themes
        for value in ['pollution', 'theme1', 'theme2']:
            concept = ThemeFactory(code=str(i))
            concept.properties.create(
                name='prefLabel', value=value, language_id='en',
                version_added=version
            )
            i += 1
        pollution_theme = Theme.objects.get_by_name('pollution')
        pollution_concept.source_relations.create(
            target=pollution_theme,
            version_added=version,
            property_type=PropertyType.objects.get(name='theme')
        )

    def test_import_concepts_and_translations_together(self):
        num_concepts_before = Concept.objects.count()
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/concepts.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url, {"synchronous": True})
        self.assertEqual(response.status_code, 200)

        # 45 new concepts were imported
        num_concepts_after = Concept.objects.count()
        self.assertEqual(num_concepts_after - num_concepts_before, 45)
        # Notes are also imported
        self.assertEqual(
            Property.objects.filter(
                name='scopeNote', value='As opposed to green finance'
            ).count(),
            1
        )
        # In all languages
        self.assertEqual(
            Property.objects.filter(
                name='scopeNote', value=u'Par opposition à la finance verte'
            ).count(),
            1
        )
        # And multiple altlabels
        self.assertEqual(
            Property.objects.filter(name='altLabel').filter(
                value__in=[
                    'Net zero emissions economy',
                    'net-zero greenhouse gas emissions economy',
                    'climate neutrality economy'
                ]
            ).count(),
            3
        )
        # Multiple broader concepts, groups and themes are supported
        brown_finance = Term.objects.get_by_name('brown finance')
        self.assertEqual(
            Relation.objects.filter(
                source=brown_finance,
            ).count(),
            8
            # 2 Broader concepts, 2 Groups, 2 Themes
            # + 1 Group and 1 Theme Inherited from pollution
        )

    def test_import_concepts_and_translations_separately(self):
        num_concepts_before = Concept.objects.count()
        # Import concepts in English first
        import_obj = Import.objects.create(
            spreadsheet=File(open('gemet/thesaurus/tests/files/only_en.xlsx'))
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url, {"synchronous": True})
        self.assertEqual(response.status_code, 200)

        # 45 new concepts were imported
        num_concepts_after = Concept.objects.count()
        self.assertEqual(num_concepts_after - num_concepts_before, 45)

        num_properties_before = Property.objects.count()
        # Import a separate spreadsheet only with translations
        import_obj = Import.objects.create(
            spreadsheet=File(
                open('gemet/thesaurus/tests/files/only_translations.xlsx')
            )
        )
        url = '/import/{}/start/'.format(import_obj.pk)
        response = self.client.get(url, {"synchronous": True})
        self.assertEqual(response.status_code, 200)
        # The number of concepts is still the same
        self.assertEqual(Concept.objects.count(), num_concepts_after)
        # New properties were created with translations
        self.assertGreater(Property.objects.count(), num_properties_before)
