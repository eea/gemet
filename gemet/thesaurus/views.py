from django.shortcuts import render, get_object_or_404
from gemet.thesaurus.models import (
    Namespace,
    Property,
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


def index(request):
    return render(request, 'index.html', {})


def themes_list(request, langcode):
    ns = Namespace.objects.get(heading='Themes')
    themes = Property.objects.filter(concept__namespace=ns, name='prefLabel')

    return render(request, 'themes_list.html', {'themes': themes})


def groups_list(request, langcode):
    languages = Language.objects.values_list('code', flat=True)

    supergroups = Concept.objects.filter(namespace__heading='Super Groups')
    for supergroup in supergroups:
        _attach_attributes(supergroup, langcode)

    return render(request, 'groups_list.html', {
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
