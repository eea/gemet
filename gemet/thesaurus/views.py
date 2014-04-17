from django.shortcuts import render, get_object_or_404, redirect

from gemet.thesaurus.models import (
    Language,
    Concept,
)


def _attach_attributes(concept, langcode, expand=None):
    concept.set_attribute('prefLabel', langcode)
    concept.set_children()
    if expand is not None:
        concept.set_expand(expand)
    for child in concept.children:
        _attach_attributes(child, langcode, expand)


def redirect_old(request, view_name, id):
    get_params = request.GET.dict()
    kargs = {'langcode': get_params.pop('langcode', 'en')}
    if id:
        views_args = {'concept': 'concept_id', 'relations': 'group_id'}
        kargs.update({views_args[view_name]: id})
    response = redirect(view_name, **kargs)
    if get_params:
        response['Location'] += '?' + '&'.join([
            '{0}={1}'.format(k, v) for k, v in get_params.iteritems()])
    return response


def themes(request, langcode):
    languages = Language.objects.values_list('code', flat=True)

    themes = Concept.objects.filter(namespace__heading='Themes')
    for theme in themes:
        theme.set_attribute('prefLabel', langcode)

    return render(request, 'themes.html', {
        'languages': languages,
        'langcode': langcode,
        'themes': themes,
    })


def groups(request, langcode):
    languages = Language.objects.values_list('code', flat=True)

    supergroups = Concept.objects.filter(namespace__heading='Super Groups')
    for supergroup in supergroups:
        _attach_attributes(supergroup, langcode)

    return render(request, 'groups.html', {
        'languages': languages,
        'langcode': langcode,
        'supergroups': supergroups,
    })


def concept(request, concept_id, langcode):
    languages = Language.objects.values_list('code', flat=True)

    concept = get_object_or_404(Concept, pk=concept_id)

    for property_name in ['prefLabel', 'definition', 'scopeNote']:
        concept.set_attribute(property_name, langcode)

    for parent in ['group', 'theme']:
        concept.set_parent(parent, langcode)

    concept.translations = concept.properties.filter(name='prefLabel')

    return render(request, 'concept.html', {
        'languages': languages,
        'langcode': langcode,
        'concept': concept,
    })


def relations(request, group_id, langcode):
    languages = Language.objects.values_list('code', flat=True)

    expand_text = request.GET.get('exp')
    expand = expand_text.split('-') if expand_text else []

    group = get_object_or_404(Concept, pk=group_id)
    _attach_attributes(group, langcode, expand)

    return render(request, 'relations.html', {
        'group': group,
        'languages': languages,
        'langcode': langcode,
    })
