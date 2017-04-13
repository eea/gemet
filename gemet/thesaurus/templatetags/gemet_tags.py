import os
import unicodedata

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import urljoin

from gemet.thesaurus.models import Concept
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
def get_concept_names(search_text):
    names = search_text.split(SEARCH_SEPARATOR)
    return {
        'concept_name': names[1],
        'other_names': '; '.join([n for n in names[2:] if n])
    }


@register.simple_tag
def default_name(concept_id, status_values):
    return (
        Concept.objects.get(pk=concept_id)
        .properties.filter(
            language__code=DEFAULT_LANGCODE,
            name='prefLabel',
            status__in=status_values,
        ).first()
        .value
    )


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


@register.simple_tag
def exports(version, filename):
    exports_relative_path = os.path.join(version.identifier, filename)
    return urljoin(settings.EXPORTS_URL, exports_relative_path)
