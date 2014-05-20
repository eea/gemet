from models import Property


def search(query, langcode, language):
    return (
        Property.objects
        .filter(
            name='prefLabel',
            language__code=langcode,
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
