from django.core.management.base import BaseCommand
from django.db import connections
from gemet.thesaurus import PUBLISHED

from gemet.thesaurus.models import (
    Concept,
    Namespace,
    Property,
    Language,
    PropertyType,
    Relation,
    ForeignRelation,
    DefinitionSource,
    Version,
)


def dictfetchall(cursor, query_str):
    """Returns all rows from a cursor as a dict"""

    cursor.execute(query_str)
    column_names = [col[0] for col in cursor.description]
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]


def fix_concepts_without_theme_group_relation(version_id):
    property_types = PropertyType.objects.filter(
        name__in=['theme', 'group']
    )
    reversed_property_types = PropertyType.objects.filter(
        name__in=['themeMember', 'groupMember']
    )
    types = zip(property_types, reversed_property_types)
    property_type_broader = PropertyType.objects.get(name='broader')
    concepts = Concept.objects.filter(namespace__heading='Concepts')
    for concept in concepts:
        for property_type, reversed_property_type in types:
            relation = concept.source_relations.filter(
                property_type=property_type).first()
            if relation:
                continue
            broader_relation = concept.source_relations.filter(
                property_type=property_type_broader).first()
            if not broader_relation:
                continue
            broader_relations = broader_relation.target.source_relations \
                .filter(property_type=property_type)
            for relation in broader_relations:
                Relation.objects.create(
                    source=concept,
                    target=relation.target,
                    property_type=property_type,
                    version_added_id=version_id,
                    status=PUBLISHED)
                Relation.objects.create(
                    source=relation.target,
                    target=concept,
                    property_type=reversed_property_type,
                    version_added_id=version_id,
                    status=PUBLISHED)


class Command(BaseCommand):
    help = 'Import a set of terms into the database'

    def handle(self, *args, **options):
        ns_ids = Namespace.objects.values_list('id', flat=True)
        ns_str = ', '.join([str(id) for id in ns_ids])

        langcodes = (
            list(Language.objects.values_list('code', flat=True)) + ['zh'])
        langcodes_str = ', '.join(["'{0}'".format(code) for code in langcodes])

        cursor = connections['import'].cursor()
        version_id = Version.objects.get(is_current=True).id

        query_str = (
            "SELECT ns AS namespace_id, "
            "id_concept AS code, "
            "datent AS date_entered, "
            "datchg as date_changed "
            "FROM concept "
            "WHERE ns IN ({0})".format(ns_str)
        )
        rows = dictfetchall(cursor, query_str)
        for row in rows:
            row['version_added_id'] = version_id
            row['status'] = PUBLISHED
        self.import_rows(rows, Concept)
        self.warn_ignored_rows(cursor, 'concept', len(rows))
        self.stdout.write('\n')

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
            row['version_added_id'] = version_id
            row['status'] = PUBLISHED
            row['is_resource'] = row['is_resource'] or 0
            if row['language_id'] == 'zh':
                row['language_id'] = 'zh-CN'

        self.import_rows(rows, Property)
        self.warn_ignored_rows(cursor, 'property', len(rows))
        self.stdout.write('\n')

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
                row['version_added_id'] = version_id
                row['status'] = PUBLISHED
            except KeyError:
                return False
            return True

        rows = filter(update_values, rows)

        self.import_rows(rows, Relation)
        self.warn_ignored_rows(cursor, 'relation', len(rows))
        self.stdout.write('\n')

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
            row['version_added_id'] = version_id
            row['status'] = PUBLISHED

        self.import_rows(rows, ForeignRelation)
        self.warn_ignored_rows(cursor, 'foreign_relation', len(rows))
        self.stdout.write('\n')

        query_str = "SELECT * FROM definition_sources;"
        rows = dictfetchall(cursor, query_str)

        self.import_rows(rows, DefinitionSource)
        fix_concepts_without_theme_group_relation(version_id)
        self.stdout.write('\n')

    def import_rows(self, rows, model_cls):
        if rows:
            table_name = model_cls._meta.db_table

            self.stdout.write('Truncating `{0}` ...'.format(table_name))
            model_cls.objects.all().delete()

            cursor = connections['default'].cursor()
            reset_index = "ALTER TABLE {0} AUTO_INCREMENT=1".format(table_name)
            cursor.execute(reset_index)

            self.stdout.write('Inserting {0} new rows ...'.format(len(rows)))
            new_rows = [model_cls(**row) for row in rows]
            model_cls.objects.bulk_create(new_rows, batch_size=10000)
        else:
            self.stderr.write('0 rows found in the import table. Aborting ...')

    def warn_ignored_rows(self, cursor, table_name, inserted_rows_cnt):
        cursor.execute("SELECT count(*) FROM {0}".format(table_name))
        total_rows_cnt = cursor.fetchone()[0]
        ignored_rows_cnt = total_rows_cnt - inserted_rows_cnt
        self.stdout.write('{0} rows ignored.'.format(ignored_rows_cnt))
