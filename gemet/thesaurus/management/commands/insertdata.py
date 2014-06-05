from django.core.management.base import BaseCommand
from datetime import datetime

from gemet.thesaurus.models import Property, Concept, Language

SEARCH_FIELDS = ['prefLabel', 'altLabel', 'notation', 'hiddenLabel']
SEPARATOR = '|'


class Command(BaseCommand):
    help = 'Insert new properties that allow searching in thesaurus'

    def handle(self, *args, **options):
        concept_ids = set(Concept.objects.values_list('id', flat=True))
        language_codes = Language.objects.values_list('code', flat=True)
        new_properties = []

        for language_code in language_codes:
            search_concept_ids = set(
                Property.objects
                .filter(
                    name='searchText',
                    language_id=language_code
                )
                .values_list('concept_id', flat=True)
            )
            concepts_without_searchtext = concept_ids - search_concept_ids

            for concept_id in concepts_without_searchtext:
                search_properties = (
                    Property.objects
                    .filter(
                        concept_id=concept_id,
                        name__in=SEARCH_FIELDS,
                        language_id=language_code,
                    )
                    .values_list('value', flat=True)
                )

                search_text = SEPARATOR.join(search_properties)
                if not search_text:
                    continue

                search_text = SEPARATOR + search_text + SEPARATOR
                search_property = Property(
                    concept_id=concept_id,
                    language_id=language_code,
                    name='searchText',
                    value=search_text,
                    is_resource=0,
                )
                new_properties.append(search_property)

        if new_properties:
            self.stdout.write(
                'Inserting {0} new rows into Property table...'
                .format(len(new_properties), datetime.now())
            )
        else:
            self.stdout.write('No rows to insert.')

        Property.objects.bulk_create(new_properties, batch_size=100000)
