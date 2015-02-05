from base64 import encodestring, decodestring
from zlib import compress, decompress

from models import Property

SEPARATOR = '\t'


def is_rdf(request):
    accepts = request.META.get('HTTP_ACCEPT', '*/*')
    parts = accepts.split(',')
    return 'application/rdf+xml' in parts


def regex_search(query, language, heading):
    return (
        Property.objects
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
        Property.objects
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
        Property.objects
        .filter(
            name='searchText',
            language__code=language.code,
            concept__namespace__heading=heading,
        )
        .extra(
            where=['value like convert(_utf8%s using utf8)'],
            params=['%%' + SEPARATOR + query + '%%'],
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


def exp_encrypt(exp):
    return encodestring(compress(exp))


def exp_decrypt(exp):
    return decompress(decodestring(exp))
