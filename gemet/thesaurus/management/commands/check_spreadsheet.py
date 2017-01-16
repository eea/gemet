from optparse import make_option

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from gemet.thesaurus.models import Property

import re
import xlrd

LABELS = {
    'RT (GEMET)': True,
    'RT (new)': False,
    'BT (GEMET)': True,
    'BT (new)': False,
    'NT (GEMET)': True,
    'NT (new)': False,
}


def check_new_term_existence(new_terms, term):
    return term in new_terms


def check_term_database_existence(term):
    return Property.objects.filter(value=term).exists()


def split_text_into_terms(raw_text):

    raw_text = raw_text.strip()
    pattern = re.compile("[^a-zA-Z\d\s\-'\)''\(':]")
    term_list = pattern.split(raw_text)
    correct_term_list = []
    for term in term_list:
        correct_terms = map(lambda term: term.strip(' \t\n;,.:').lower(),
                            term.split('\n'))
        correct_terms = filter(lambda term: term != '', correct_terms)
        correct_term_list.extend(correct_terms)
    return correct_term_list


def row_idx_to_name(idx):
    result = ""
    while True:
        if idx > 26:
            idx, r = divmod(idx - 1, 26)
            result = chr(r + ord('A')) + result
        else:
            return chr(idx + ord('A') - 1) + result


def to_excel_row_column(row_idx, column_idx):
    row = row_idx_to_name(row_idx + 1)
    return row + str(column_idx + 2)


def check_term_existence(term, term_type, excel_cell_value, new_terms):
    if term_type is not None:
        message = 'Error at cell {}: "{}"'.format(excel_cell_value, term)
        if term_type:
            if not check_term_database_existence(term):
                message += ' not defined in database.'
                message += ' Term found in column "Label".' \
                    if check_new_term_existence(new_terms, term) else ''
                print message
        else:
            if not check_new_term_existence(new_terms, term):
                message += ' not found in column "Label".'
                message += ' Term found in database.' \
                    if check_term_database_existence(term) else ''
                print message


class Command(BaseCommand):
    help = 'Check if spreadsheet terms are consistent.'

    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="filename",
            help="specify excel import file",
            metavar="FILE"
        ),
    )

    def handle(self, *args, **options):
        if not options['filename']:
            raise CommandError("Option `--file=...` must be specified.")
        try:
            workbook = xlrd.open_workbook(options['filename'])
        except xlrd.XLRDError:
            print 'The file provided is not a valid excel file.'

        except IOError as e:
            print e
        else:
            sheet = workbook.sheet_by_index(0)
            new_terms_column = sheet.col_values(0, start_rowx=1)
            new_terms = []

            for name in new_terms_column:
                new_terms.append(name.strip().lower())
            labels_row = sheet.row_values(0)

            for col_idx, column_label in enumerate(labels_row):
                term_type = LABELS.get(column_label, None)
                if term_type is not None:
                    column_values = sheet.col_values(col_idx, start_rowx=1)

                    for row_idx, cell in enumerate(column_values):
                        correct_terms = split_text_into_terms(cell)
                        excel_cell_value = to_excel_row_column(col_idx, row_idx)

                        for term in correct_terms:
                            check_term_existence(term, term_type,
                                                 excel_cell_value, new_terms)
