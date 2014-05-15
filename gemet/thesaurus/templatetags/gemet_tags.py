from django import template

from gemet.thesaurus.models import Concept

from gemet.thesaurus import DEFAULT_LANGCODE


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
        'param': '-'.join(expand_copy),
        'status': expanded,
    }


@register.assignment_tag
def get_children(concept_id, langcode):
    return Concept.objects.get(pk=concept_id).get_children(langcode)


@register.simple_tag
def broader_context(concept_id, langcode):
    broader_concepts = Concept.objects.get(pk=concept_id).get_siblings(
        langcode, 'broader')
    return '; '.join([cp['name'] for cp in broader_concepts])


@register.simple_tag
def get_default_name(concept_id):
    return Concept.objects.get(pk=concept_id).properties.filter(
        language__code=DEFAULT_LANGCODE,
        name='prefLabel'
    ).first().value
