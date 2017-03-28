from django.core.management.base import BaseCommand
from gemet.thesaurus import PUBLISHED
from gemet.thesaurus.models import Property, Concept, Language, Version
from gemet.thesaurus.utils import SEPARATOR

SEARCH_FIELDS = ['prefLabel', 'altLabel', 'notation', 'hiddenLabel']


class Command(BaseCommand):
    help = 'Insert new properties that allow searching in thesaurus'

    def handle(self, *args, **options):
        concept_ids = set(Concept.objects.values_list('id', flat=True))
        language_codes = Language.objects.values_list('code', flat=True)
        version = Version.objects.get(is_current=True)
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
                    .values_list('name', 'value')
                )

                if not search_properties:
                    continue

                search_dict = dict(search_properties)
                search_text = SEPARATOR.join(
                    [search_dict.get(field, '') for field in SEARCH_FIELDS])

                search_text = SEPARATOR + search_text + SEPARATOR
                search_property = Property(
                    concept_id=concept_id,
                    language_id=language_code,
                    name='searchText',
                    value=search_text,
                    is_resource=0,
                    status=PUBLISHED,
                    version_added_id=version.id
                )
                new_properties.append(search_property)

        if new_properties:
            self.stdout.write(
                'Inserting {0} new rows into Property table...'
                .format(len(new_properties))
            )
        else:
            self.stdout.write('No rows to insert.')

        Property.objects.bulk_create(new_properties, batch_size=100000)
