from django.core.management.base import BaseCommand
from django.db import connections

from gemet.thesaurus.models import (
    Concept,
    Namespace,
    Property,
    Language,
    PropertyType,
    Relation,
    ForeignRelation,
    DefinitionSource,
)


def dictfetchall(cursor, query_str):
    """Returns all rows from a cursor as a dict"""

    cursor.execute(query_str)
    column_names = [col[0] for col in cursor.description]
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]


class Command(BaseCommand):
    help = 'Import a set of terms into the database'

    def handle(self, *args, **options):
        ns_ids = Namespace.objects.values_list('id', flat=True)
        ns_str = ', '.join([str(id) for id in ns_ids])

        langcodes = Language.objects.values_list('code', flat=True)
        langcodes_str = ', '.join(["'{0}'".format(code) for code in langcodes])

        cursor = connections['import'].cursor()

        query_str = (
            "SELECT ns AS namespace_id, "
            "id_concept AS code, "
            "datent AS date_entered, "
            "datchg as date_changed "
            "FROM concept "
            "WHERE ns IN ({0})".format(ns_str)
        )
        rows = dictfetchall(cursor, query_str)

        self.import_rows(rows, 'thesaurus_concept', Concept)

        query_str = (
            "SELECT concat(ns, id_concept) AS concept_id, "
            "langcode AS language_id, "
            "name, "
            "value, "
            "is_resource "
            "FROM property "
            "WHERE ns IN ({0}) "
            "AND langcode IN ({1})"
            .format(ns_str, langcodes_str)
        )
        rows = dictfetchall(cursor, query_str)

        concept_ids = {'{0}{1}'.format(c.namespace.id, c.code): c.id
                       for c in Concept.objects.all()}
        for row in rows:
            row['concept_id'] = concept_ids[row['concept_id']]

        self.import_rows(rows, 'thesaurus_property', Property)

        query_str = (
            "SELECT concat(source_ns, id_concept) AS source_id, "
            "concat(target_ns, id_relation) AS target_id, "
            "id_type AS property_type_id "
            "FROM relation "
            "WHERE source_ns IN ({0}) "
            "AND target_ns IN ({0}) "
            .format(ns_str)
        )
        rows = dictfetchall(cursor, query_str)

        property_ids = {p.name: p.id for p in PropertyType.objects.all()}

        def update_values(row):
            try:
                row['source_id'] = concept_ids[row['source_id']]
                row['target_id'] = concept_ids[row['target_id']]
                row['property_type_id'] = property_ids[row['property_type_id']]
            except KeyError:
                return False
            return True

        rows = filter(update_values, rows)

        self.import_rows(rows, 'thesaurus_relation', Relation)

        query_str = (
            "SELECT concat(source_ns, id_concept) AS concept_id, "
            "relation_uri AS uri, "
            "id_type AS property_type_id, "
            "label, "
            "show_in_html "
            "FROM foreign_relation "
            "WHERE source_ns IN ({0}) "
            .format(ns_str)
        )
        rows = dictfetchall(cursor, query_str)

        for row in rows:
            row['concept_id'] = concept_ids[row['concept_id']]
            row['property_type_id'] = property_ids[row['property_type_id']]

        self.import_rows(rows, 'thesaurus_foreignrelation', ForeignRelation)

        query_str = "SELECT * FROM definition_sources;"
        rows = dictfetchall(cursor, query_str)

        self.import_rows(rows, 'thesaurus_definitionsource', DefinitionSource)

    def import_rows(self, rows, table_name, model_cls):
        if rows:
            self.stdout.write('Truncating `{0}` ...'.format(table_name))
            model_cls.objects.all().delete()

            cursor = connections['default'].cursor()
            reset_index = "ALTER TABLE {0} AUTO_INCREMENT=1".format(table_name)
            cursor.execute(reset_index)

            self.stdout.write('Inserting {0} new rows ...'.format(len(rows)))
            new_rows = [model_cls(**row) for row in rows]
            model_cls.objects.bulk_create(new_rows, batch_size=100000)
        else:
            self.stderr.write('0 rows found in the import table. Aborting ...')
