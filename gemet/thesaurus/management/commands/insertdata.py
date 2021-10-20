from django.core.management.base import BaseCommand
from gemet.thesaurus import PUBLISHED
from gemet.thesaurus.models import Property, Concept, Language, Version
from gemet.thesaurus.utils import get_search_text

SEARCH_FIELDS = ["prefLabel", "altLabel", "notation", "hiddenLabel"]


class Command(BaseCommand):
    help = "Insert new properties that allow searching in thesaurus"

    def handle(self, *args, **options):
        concept_ids = set(Concept.objects.values_list("id", flat=True))
        language_codes = Language.objects.values_list("code", flat=True)
        version = Version.objects.get(is_current=True)

        for language_code in language_codes:

            new_properties = []
            search_concept_ids = set(
                Property.objects.filter(
                    name="searchText", language_id=language_code
                ).values_list("concept_id", flat=True)
            )
            concepts_without_searchtext = concept_ids - search_concept_ids
            for concept_id in concepts_without_searchtext:
                search_property = get_search_text(
                    concept_id, language_code, PUBLISHED, version
                )
                if search_property:
                    new_properties.append(search_property)

            if new_properties:
                self.stdout.write(
                    "Inserting {0} new rows into Property table for lang {1}...".format(
                        len(new_properties), language_code
                    )
                )
            else:
                self.stdout.write(
                    "No rows to insert for lang {0}.".format(language_code)
                )

            Property.objects.bulk_create(new_properties, batch_size=10000)
