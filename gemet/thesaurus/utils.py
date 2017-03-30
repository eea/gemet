from base64 import encodestring, decodestring
from zlib import compress, decompress

from gemet.thesaurus.models import Property, PropertyType, Relation, Version
from gemet.thesaurus import RELATION_PAIRS

SEPARATOR = '\t'


def is_rdf(request):
    accepts = request.META.get('HTTP_ACCEPT', '*/*')
    parts = accepts.split(',')
    return 'application/rdf+xml' in parts


def regex_search(query, language, heading):
    return (
        Property.published
        .filter(
            name='prefLabel',
            language__code=language.code,
            concept__namespace__heading=heading,
            value__iregex=r'%s' % query,
        )
        .extra(
            select={
                'value_coll': 'value COLLATE {0}'.format(language.charset),
                'name': 'value',
                'id': 'concept_id',
            },
            order_by=['value_coll']
        )
        .values('id', 'concept__code', 'name')
    )


def search_queryset(query, language, search_mode=1, heading='Concepts',
                    api_call=False):
    if api_call:
        if search_mode == 4:
            values = (
                api_search(query, language, 0, heading) or
                api_search(query, language, 1, heading) or
                api_search(query, language, 2, heading) or
                api_search(query, language, 3, heading)
            )
        else:
            values = api_search(query, language, search_mode, heading)
    else:
        values = insite_search(query, language, heading)

    return values


def api_search(query, language, search_mode, headings):
    search_types = {
        0: [query],
        1: [query + '%%'],
        2: ['%%' + query],
        3: ['%%' + query + '%%']
    }
    query_search = search_types.get(search_mode)

    return (
        Property.published
        .filter(
            name='prefLabel',
            language__code=language.code,
            concept__namespace__heading__in=headings,
        )
        .extra(
            where=['value like convert(_utf8%s using utf8)'],
            params=query_search,
        )
        .extra(
            select={
                'value_coll': 'value COLLATE {0}'.format(language.charset),
                'name': 'value',
                'id': 'concept_id',
            },
            order_by=['value_coll']
        )
        .values('id', 'concept__code', 'name')
    )


def insite_search(query, language, heading):

    return (
        Property.published
        .filter(
            name='searchText',
            language__code=language.code,
            concept__namespace__heading=heading,
        )
        .extra(
            where=['value like convert(_utf8%s using utf8)'],
            params=['%%' + query + '%%'],
        )
        .extra(
            select={
                'search_text': 'value COLLATE {0}'.format(language.charset),
                'id': 'concept_id',
            },
            order_by=['search_text']
        )
        .values('id', 'search_text', 'concept__code')
    )


def get_version_choices():
    current_identifier = Version.objects.get(is_current=True).identifier
    major, middle, minor = map(int, current_identifier.split("."))
    choices = (
        ".".join(map(str, version_parts)) for version_parts in (
            (major, middle, minor+1),
            (major, middle+1, 0),
            (major+1, 0, 0),
        )
    )
    return ((choice, choice) for choice in choices)


def exp_encrypt(exp):
    return encodestring(compress(exp))


def exp_decrypt(exp):
    return decompress(decodestring(exp))


def has_reverse_relation(relation):
    return (
        Relation.objects
        .filter(source=relation.target, target=relation.source)
        .exists()
    )


def create_reverse_relation(relation):
    reverse_relation = PropertyType.objects.get(
        name=RELATION_PAIRS[relation.property_type.name])

    Relation.objects.create(
        source=relation.target,
        target=relation.source,
        property_type=reverse_relation,
        status=relation.status,
        version_added=relation.version_added,
    )


def get_form_errors(errors):
    # errors is a dictionary with a list as value for each key;
    # the function returns the a string with all the values flattened
    return ' '.join([''.join(error) for error in errors.values()])
