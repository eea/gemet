from base64 import encodestring, decodestring
from zlib import compress, decompress

from models import Property


def search_queryset(query, language):
    return (
        Property.objects
        .filter(
            name='prefLabel',
            language__code=language.code,
            concept__namespace__heading='Concepts',
        )
        .extra(
            where=['value like convert(_utf8%s using utf8)'],
            params=[query + '%%'],
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


def exp_encrypt(exp):
    return encodestring(compress(exp))


def exp_decrypt(exp):
    return decompress(decodestring(exp))
