from gemet.thesaurus import PUBLISHED, PENDING, SEARCH_SEPARATOR
from gemet.thesaurus.models import Property

SEARCH_FIELDS = ['prefLabel', 'altLabel', 'notation', 'hiddenLabel']


def get_search_text(concept_id, language_code, status, version):
    search_properties = (
        Property.objects
        .filter(
            concept_id=concept_id,
            language_id=language_code,
            name__in=SEARCH_FIELDS,
            status__in=[PUBLISHED, PENDING]
        )
        .values_list('value', flat=True)
    )

    if not search_properties:
        return

    search_text = SEARCH_SEPARATOR.join(search_properties)
    search_text = SEARCH_SEPARATOR + search_text + SEARCH_SEPARATOR

    return Property(
        concept_id=concept_id,
        language_id=language_code,
        name='searchText',
        value=search_text,
        is_resource=0,
        status=status,
        version_added_id=version.id
    )
