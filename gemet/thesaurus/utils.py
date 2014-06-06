from base64 import encodestring, decodestring
from zlib import compress, decompress

from models import Property

SEPARATOR = '\t'


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
            select={'value_coll': 'value COLLATE {0}'.format(
                language.charset)},
        )
        .extra(
            select={
                'name': 'value',
                'id': 'concept_id'
            })
        .extra(
            order_by=['value_coll']
        )
        .values('id', 'name')
    )


def search_queryset(query, language, search_mode=1, heading='Concepts',
                    api_call=False):

    if api_call:
        if search_mode == 4:
            values = search_queryset_mode(query, language, 0, heading) or \
                search_queryset_mode(query, language, 1, heading) or \
                search_queryset_mode(query, language, 2, heading) or \
                search_queryset_mode(query, language, 3, heading)
        else:
            values = search_queryset_mode(query, language, search_mode,
                                          heading)
    else:
        values = search_queryset_mode(query, language, search_mode, heading)

    return values


def search_queryset_mode(query, language, search_mode, heading):
    search_types = {
        0: ['%%' + SEPARATOR + query + SEPARATOR + '%%'],
        1: ['%%' + SEPARATOR + query + '%%'],
        2: ['%%' + query + SEPARATOR + '%%'],
        3: ['%%' + query + '%%'],
    }
    query_search = search_types.get(search_mode)
    if not query_search:
        return set([])

    return (
        Property.objects
        .filter(
            name='searchText',
            language__code=language.code,
            concept__namespace__heading=heading,
        )
        .extra(
            where=['value like convert(_utf8%s using utf8)'],
            params=query_search,
        )
        .extra(
            select={
                'search_text': 'value COLLATE {0}'.format(language.charset),
                'id': 'concept_id',
            })
        .extra(order_by=['search_text'])
        .values('id', 'search_text')
    )


def exp_encrypt(exp):
    return encodestring(compress(exp))


def exp_decrypt(exp):
    return decompress(decodestring(exp))
