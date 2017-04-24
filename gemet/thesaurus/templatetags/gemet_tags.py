import unicodedata

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from gemet.thesaurus.models import Concept, Language, Property
from gemet.thesaurus import DEFAULT_LANGCODE, SEARCH_SEPARATOR, EDIT_URL_NAMES
from gemet.thesaurus.utils import exp_encrypt


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
def get_children(concept_id, langcode, status_values):
    concept = Concept.objects.get(pk=concept_id)
    concept.status_list = status_values
    return concept.get_children(langcode)


@register.assignment_tag
def get_broader_context(concept_id, langcode, status_values):
    concept = Concept.objects.get(pk=concept_id)
    concept.status_list = status_values
    broader_concepts = concept.get_siblings(langcode, 'broader')
    return '; '.join([cp['name'] for cp in broader_concepts])


@register.assignment_tag
def get_concept_names(concept, status_values, langcode):
    name = Property.objects.get(name='prefLabel',
                                status__in=status_values,
                                concept_id=concept['id'],
                                language=langcode).value
    names = concept['search_text'].split(SEARCH_SEPARATOR)
    return {
        'concept_name': name,
        'other_names': '; '.join([n for n in names if n and n != name])
    }


@register.simple_tag
def get_concept_name(concept_name, concept_id, status_values):
    if concept_name:
        return concept_name
    concept = (
        Concept.objects.get(pk=concept_id)
        .properties.filter(
            language__code=DEFAULT_LANGCODE,
            name='prefLabel',
            status__in=status_values,
        ).first()
    )
    if concept:
        language = Language.objects.get(code=DEFAULT_LANGCODE).name.lower()
        return mark_safe(concept.value + ' <span>[' + language + ']</span>')
    else:
        return ''


@register.simple_tag
def get_url(concept_code, langcode, namespace):
    return reverse(EDIT_URL_NAMES[namespace],
                   kwargs={'langcode': langcode, 'code': concept_code})


@register.filter
def normalize(value, form):
    return unicodedata.normalize(form, value)


@register.filter
def getattr(obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    (attribute, default) = args.split(',') if ',' in args else (args, None)
    try:
        return obj.__getattribute__(attribute)
    except AttributeError:
        return obj.__dict__.get(attribute, default)
    except:
        return default


@register.simple_tag
def active(request, name, **kwargs):
    """ Return the string 'active' current request.path is same as the reverse
    of name and its arguments

    Aruguments:
    request  -- Django request object
    name     -- name of the url or the actual path
    kwargs   -- arguments of the url
    """
    path = reverse(name, kwargs=kwargs)

    if request.path == path:
        return ' active '

    return ''
