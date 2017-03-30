from django.core.management.base import BaseCommand

from gemet.thesaurus.models import Concept
from gemet.thesaurus.utils import has_reverse_relation, create_reverse_relation


class Command(BaseCommand):
    help = 'Fix unidirectional relationships'

    def handle(self, *args, **options):
        relations = []
        for cp in Concept.objects.all():
            if cp.source_relations.count() != cp.target_relations.count():
                relations.extend(list(cp.source_relations.all()))
                relations.extend(list(cp.target_relations.all()))

        for relation in relations:
            if not has_reverse_relation(relation):
                self.stdout.write('Creating reverse relation for {}'
                                  .format(relation))
                create_reverse_relation(relation)
