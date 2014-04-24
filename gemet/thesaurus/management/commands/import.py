from django.core.management.base import BaseCommand
from django.db import connections

from gemet.thesaurus.models import Concept, Namespace


def dictfetchall(cursor):
    """Returns all rows from a cursor as a dict"""

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class Command(BaseCommand):
    help = 'Import a set of terms into the database'

    def handle(self, *args, **options):
        ns_ids = Namespace.objects.values_list('id', flat=True)
        ns_str = ', '.join([str(id) for id in ns_ids])

        cursor = connections['import'].cursor()

        query_str = (
            "SELECT ns AS namespace_id, "
            "id_concept AS code, "
            "datent AS date_entered, "
            "datchg as date_changed "
            "FROM concept "
            "WHERE ns IN ({0})".format(ns_str)
        )

        cursor.execute(query_str)
        rows = dictfetchall(cursor)

        if rows:
            self.stdout.write('Truncating `thesaurus_concept` ...')
            Concept.objects.all().delete()

            cursor_default = connections['default'].cursor()
            reset_index = "ALTER TABLE thesaurus_concept AUTO_INCREMENT=1"
            cursor_default.execute(reset_index)

            self.stdout.write('Inserting {0} new rows ...'.format(len(rows)))
            concepts = [Concept(**row) for row in rows]
            Concept.objects.bulk_create(concepts)
        else:
            self.stderr.write('0 rows found in the import table. Aborting ...')
