from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from django.db import transaction
from django.utils import timezone

from gemet.thesaurus import PENDING, PUBLISHED
from gemet.thesaurus.models import (
    Namespace, Version, Concept, Property, PropertyType, Relation, Language
)
from gemet.thesaurus.utils import get_new_code, get_search_text


class ImportError(Exception):
    pass


def namespace_for(property_type_name):
    heading_for = {
        'broader': 'Concepts',
        'group': 'Groups',
    }
    return Namespace.objects.get(
        heading=heading_for[property_type_name]
    )


def row_dicts(sheet):
    rows = sheet.rows

    mandatory_columns = {
        "Term", "Definition", "Definition reference"
    }
    optional_columns = {
        "Alt Label", "Abbreviation/Alt Label", "Synonym/Alt Label",
        "Broader concept", "Broader URI", "Group", "Note"
    }
    optional_columns.add(sheet.title)
    supported_columns = mandatory_columns.union(optional_columns)
    column_names = [
        c.value.strip() for c in next(rows) if c.value and c.value.strip()
    ]

    for column in mandatory_columns:
        if column not in column_names:
            raise ImportError(u'Column "{}" is mandatory.'.format(column))

    for column in column_names:
        if column not in supported_columns:
            raise ImportError(u'Column "{}" is not supported.'.format(column))

    for row in rows:
        values = [(c.value or '').strip() for c in row[1:]]
        if not ''.join(values).strip():
            # The sheet is over, there are only empty rows now.
            return
        yield dict(zip(column_names, values))


class Importer(object):

    def __init__(self, import_obj):
        self.import_obj = import_obj

    @transaction.atomic
    def import_file(self):
        self.concept_ns = Namespace.objects.get(heading='Concepts')
        self.group_ns = Namespace.objects.get(heading='Groups')
        # Number of regular concepts before
        num_reg_concepts_bef = Concept.objects.filter(
            namespace=self.concept_ns
        ).count()
        # Number of group concepts before
        num_groups_bef = Concept.objects.filter(namespace=self.group_ns).count()

        try:
            print("Opening file...")
            wb = load_workbook(filename=self.import_obj.spreadsheet.path)
        except InvalidFileException:
            raise ImportError('The file provided is not a valid excel file.')
        except IOError:
            raise ImportError('The file provided does not exist.')

        # Get the version with no name, used for pending concepts
        self.version = Version.under_work()
        # Keep a cache with a reference to all created concepts
        self.concepts = {}
        # The first sheet must have the original English concepts
        concepts_sheetname = wb.sheetnames[0]
        # All other sheets must have translations
        translation_sheetnames = wb.sheetnames[1:]

        print('Creating concepts...')
        self._create_concepts(wb[concepts_sheetname])

        print('Creating relations...')
        self._create_relations(wb[concepts_sheetname])

        num_reg_concepts_after = Concept.objects.filter(
            namespace=self.concept_ns
        ).count()
        num_groups_after = Concept.objects.filter(
            namespace=self.group_ns
        ).count()

        report = "Created {} regular concepts and {} group concepts.".format(
            num_reg_concepts_after - num_reg_concepts_bef,
            num_groups_after - num_groups_bef,
        )

        if translation_sheetnames:
            print('Creating translations...')
            for sheetname in translation_sheetnames:
                print('    {}...'.format(sheetname))
                self._add_translations(wb[sheetname])

            report += (
                "\n\nTranslations for the following {} languages"
                " were also created: {}."
            ).format(
                len(translation_sheetnames),
                ', '.join(translation_sheetnames)
            )

        return report

    def _create_concepts(self, sheet):
        for i, row in enumerate(row_dicts(sheet)):
            label = row.get("Term")  # aka prefLabel
            if not label:
                raise ImportError(u'Row {} has no "Term".'.format(i))

            alt_labels = [row[key] for key in row.keys() if 'Alt Label' in key]
            defin = row.get("Definition")
            source = row.get("Definition source")

            property_values = {
                'prefLabel': label,
                'definition': defin,
                'source': source,
            }

            if alt_labels:
                property_values['altLabels'] = alt_labels

            # A concept must always have at least an English property, so if
            # there is no English property corresponding to that term in the
            # DB, the concept must be new.
            prop = Property.objects.filter(
                name='prefLabel',
                value__iexact=label,
                language_id='en',
            ).first()

            if prop:
                is_new_concept = False
                concept = prop.concept
                msg = u'Concept {} exists. '.format(label)
                if prop.status in [PENDING, PUBLISHED]:
                    del property_values['prefLabel']
                    msg += 'Skipping prefLabel creation.'
                print(msg)
            else:
                is_new_concept = True
                code = get_new_code(self.concept_ns)

                concept = Concept.objects.create(
                    code=code,
                    namespace=self.concept_ns,
                    version_added=self.version,
                    status=PENDING,
                    date_entered=timezone.now(),
                )
                print(u'Concept added: {}'.format(label))

            self.concepts[label.lower()] = concept

            concept.update_or_create_properties(property_values)

            if is_new_concept:
                # Create internal "searchText" property with the concatenated
                # values from all other concept properties.
                search_text = get_search_text(
                    concept.id, 'en', PENDING, self.version
                )
                if search_text:
                    search_text.save()

    def _create_relations(self, sheet):

        property_types = PropertyType.objects.filter(
            name__in=['broader', 'group']
        )

        for i, row in enumerate(row_dicts(sheet)):

            source_label = row.get("Term")  # aka prefLabel

            for property_type in property_types:

                # Look for columns specifying relationships
                if property_type.name == 'broader':
                    target_label = row.get("Broader concept")
                elif property_type.name == 'group':
                    target_label = row.get("Group")

                if not target_label:
                    # If it doesn't exist, there is no relation to be created
                    print(
                        (
                            'Row {} has neither "broader" nor "group" columns.'
                        ).format(i)
                    )
                    continue

                source = self.concepts[source_label.lower()]
                target = self._get_concept(target_label)
                namespace = namespace_for(property_type.name)

                if not target:
                    print(
                        'Creating inexistent concept: {}'.format(target_label)
                    )
                    code = get_new_code(self.concept_ns)
                    target = Concept.objects.create(
                        code=code,
                        namespace=namespace,
                        version_added=self.version,
                        status=PENDING,
                        date_entered=timezone.now(),
                    )
                    target.properties.create(
                        status=PENDING,
                        version_added=self.version,
                        language_id='en',
                        name='prefLabel',
                        value=target_label,
                    )

                # target is broader of source
                relation = Relation.objects.filter(
                    source=source,
                    target=target,
                    property_type=property_type,
                ).first()

                if not relation:
                    relation = Relation.objects.create(
                        source=source,
                        target=target,
                        property_type=property_type,
                        version_added=self.version,
                        status=PENDING,
                    )
                    print('Relation created: {}'.format(relation))

                if not relation.reverse:
                    reverse_relation = relation.create_reverse()
                    print(
                        'Reverse relation created: {}'.format(reverse_relation)
                    )

    def _add_translations(self, sheet):
        for row in row_dicts(sheet):

            language = Language.objects.get(code=sheet.title.lower())

            en_label = row.get('Term')
            foreign_label = row.get(sheet.title)
            definition = row.get('Definition')

            if not en_label:
                raise ImportError(u'"Term" column cannot be blank.')

            property_values = {
                'prefLabel': foreign_label,
                'definition': definition,
            }

            concept = Property.objects.get(
                name='prefLabel',
                value__iexact=en_label,
                language=Language.objects.get(code='en'),
            ).concept

            concept.update_or_create_properties(
                property_values, language_id=language.code
            )

    def _get_concept(self, label):
        concept = self.concepts.get(label.lower())

        if not concept:
            try:
                concept = Property.objects.get(
                    name='prefLabel',
                    value__iexact=label,
                    language_id='en',
                    concept__namespace=self.concept_ns,
                ).concept
            except Property.DoesNotExist:
                concept = None

        return concept
