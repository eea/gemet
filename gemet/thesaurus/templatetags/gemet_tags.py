from django import template

from gemet.thesaurus.models import Concept
from gemet.thesaurus import DEFAULT_LANGCODE
from gemet.thesaurus.utils import exp_encrypt, SEPARATOR


register = template.Library()


@register.assignment_tag
def get_expand(concept_id, expand_list):
    str_id = str(concept_id)
    expand_copy = expand_list[:]
    if str_id in expand_list:
        expanded = True
        expand_copy.remove(str_id)
    else:
        expanded = False
        expand_copy.append(str_id)

    return {
        'param': exp_encrypt('-'.join(expand_copy)),
        'status': expanded,
    }


@register.assignment_tag
def get_children(concept_id, langcode):
    return Concept.objects.get(pk=concept_id).get_children(langcode)


@register.assignment_tag
def get_broader_context(concept_id, langcode):
    broader_concepts = Concept.objects.get(pk=concept_id).get_siblings(
        langcode, 'broader')
    return '; '.join([cp['name'] for cp in broader_concepts])


@register.assignment_tag
def get_concept_names(search_text):
    names = search_text.split(SEPARATOR)
    return {
        'concept_name': names[1],
        'other_names': '; '.join([n for n in names[2:] if n])
    }


@register.simple_tag
def default_name(concept_id):
    return (
        Concept.objects.get(pk=concept_id)
        .properties.get(
            language__code=DEFAULT_LANGCODE,
            name='prefLabel',
        )
        .value
    )
