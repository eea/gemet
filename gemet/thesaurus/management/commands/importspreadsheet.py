from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from gemet.thesaurus import PENDING, PUBLISHED
from gemet.thesaurus import models
from gemet.thesaurus.utils import get_new_code, split_text_into_terms
from gemet.thesaurus.utils import has_reverse_relation, create_reverse_relation

NAMESPACE = 'Concepts'
LANGCODE = 'en'


class Command(BaseCommand):
    help = 'Import new concepts from Excel spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument('excel_file')

    def handle(self, *args, **options):
        try:
            wb = load_workbook(filename=options['excel_file'])
        except InvalidFileException:
            raise CommandError('The file provided is not a valid excel file.')
        except IOError:
            raise CommandError('The file provided does not exist.')

        sheet = wb.active
        self.language = models.Language.objects.get(code=LANGCODE)
        self.version = models.Version.under_work()
        self.namespace = models.Namespace.objects.get(heading=NAMESPACE)

        self.stdout.write('Creating concepts...')
        self._create_concepts(sheet)
        self.stdout.write('Creating relations...')
        self._create_relations(sheet)

    def _create_concepts(self, sheet):
        for row in sheet.iter_rows(max_col=3, min_row=2):
            label, definition, source = [(cell.value or '').strip()
                                         for cell in row]

            if not label:
                continue

            property = models.Property.objects.filter(
                name='prefLabel',
                value=label,
                language=self.language,
            ).first()

            skip_pref = False

            if property:
                concept = property.concept
                self.stdout.write(u'Concept {} exists'.format(label))
                if property.status in [PENDING, PUBLISHED]:
                    skip_pref = True
                    self.stdout.write('Skipping prefLabel creation')
            else:
                code = get_new_code(self.namespace)

                concept = models.Concept.objects.create(
                    code=code,
                    namespace=self.namespace,
                    version_added=self.version,
                    status=PENDING,
                )
                self.stdout.write(u'Concept added: {}'.format(label))

            properties = {
                'prefLabel': label,
                'definition': definition,
                'source': source,
            }
            for name, value in properties.iteritems():
                if skip_pref and name == 'prefLabel':
                    continue
                models.Property.objects.create(
                    status=PENDING,
                    version_added=self.version,
                    concept=concept,
                    language=self.language,
                    name=name,
                    value=value,
                )
            self.stdout.write(u'Properties added for: {}'.format(label))

    def _create_relations(self, sheet):
        def get_terms(row, idx1, idx2):
            text = (row[idx1].value or '') + ';' + (row[idx2].value or '')
            return split_text_into_terms(text)

        related = models.PropertyType.objects.get(name='related')
        broader = models.PropertyType.objects.get(name='broader')
        narrower = models.PropertyType.objects.get(name='narrower')

        for row in sheet.iter_rows(min_row=2):
            label = (row[0].value or '').strip()

            if not label:
                continue

            relations = {
                related: get_terms(row, 3, 4),
                broader: get_terms(row, 5, 6),
                narrower: get_terms(row, 7, 8),
            }

            source = (
                models.Property.objects
                .get(name='prefLabel', value=label, language=self.language)
                .concept
            )

            for property_type, terms in relations.iteritems():
                for term in terms:
                    try:
                        target = (
                            models.Property.objects
                            .get(
                                name='prefLabel',
                                value=term,
                                language=self.language,
                                concept__namespace=self.namespace,
                            )
                            .concept
                        )
                    except models.Property.DoesNotExist:
                        code = get_new_code(self.namespace)
                        target = models.Concept.objects.create(
                            code=code,
                            namespace=self.namespace,
                            version_added=self.version,
                            status=PENDING,
                        )
                        models.Property.objects.create(
                            status=PENDING,
                            version_added=self.version,
                            concept=target,
                            language=self.language,
                            name='prefLabel',
                            value=term,
                        )
                        self.stdout.write('Inexistent concept: {}'.format(term))

                    relation = models.Relation.objects.filter(
                        source=source,
                        target=target,
                        property_type=property_type,
                    ).first()

                    if not relation:
                        relation = models.Relation.objects.create(
                            source=source,
                            target=target,
                            property_type=property_type,
                            version_added=self.version,
                            status=PENDING,
                        )
                        self.stdout.write('Relation created: {}'.format(relation))

                if not has_reverse_relation(relation):
                    reverse_relation = create_reverse_relation(relation)
                    self.stdout.write('Reverse relation created: {}'
                                      .format(reverse_relation))
