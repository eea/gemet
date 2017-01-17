from django.core.management.base import BaseCommand
from gemet.thesaurus.models import Property

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

import re


LABELS = {
    'RT (GEMET)': True,
    'RT (new)': False,
    'BT (GEMET)': True,
    'BT (new)': False,
    'NT (GEMET)': True,
    'NT (new)': False,
}


def check_term_database_existence(term):
    return Property.objects.filter(value=term).exists()


def split_text_into_terms(raw_text):
    pattern = re.compile("[^a-zA-Z\d \-\\)\\(:]")
    term_list = pattern.split(raw_text)
    term_list = map(lambda term: term.strip(' \t\n;,.:').lower(), term_list)
    term_list = filter(lambda term: term != '', term_list)
    return term_list


class Command(BaseCommand):
    help = 'Check if spreadsheet terms are consistent.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file')

    def check_term_existence(self, term, term_type, excel_cell_value,
                             new_terms):
        message = 'Error at cell {}: "{}"'.format(excel_cell_value, term)
        if term_type:
            if not check_term_database_existence(term):
                message += ' not defined in database.'
                message += ' Term found in column "Label".' \
                    if term in new_terms else ''
                self.stdout.write(message)
        else:
            if term not in new_terms:
                message += ' not found in column "Label".'
                message += ' Term found in database.' \
                    if check_term_database_existence(term) else ''
                self.stdout.write(message)

    def handle(self, *args, **options):
        try:
            wb = load_workbook(filename=options['excel_file'])
        except InvalidFileException:
            self.stdout.write('The file provided is not a valid excel file.')
        except IOError:
            self.stdout.write('The file provided does not exist.')
        else:
            sheet = wb.active
            new_terms = []
            for x in sheet.iter_rows(min_col=1, max_col=1, min_row=2):
                new_terms.append(x[0].value.strip().lower())
            labels = []
            for x in sheet.iter_cols(min_row=1, max_row=1, min_col=1):
                labels.append(x[0])

            for label_cell in labels:
                if label_cell.value not in LABELS:
                    continue
                term_type = LABELS.get(label_cell.value)
                column_values = [x[0] for x in
                                 sheet.iter_rows(min_col=label_cell.col_idx,
                                                 max_col=label_cell.col_idx,
                                                 min_row=2)]
                for cell in column_values:
                    if not cell.value:
                        continue
                    correct_terms = split_text_into_terms(cell.value)
                    for term in correct_terms:
                        self.check_term_existence(term, term_type,
                                                  cell.coordinate, new_terms)
