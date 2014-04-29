from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from itertools import chain

from gemet.thesaurus.models import (
    Language,
    Concept,
)
from collation_charts import unicode_character_map


NR_CONCEPTS_ON_PAGE = 20
DEFAULT_LANGCODE = 'en'


def _attach_attributes(concept, langcode, expand):
    concept.set_attribute('prefLabel', langcode)
    concept.set_expand(expand)
    if concept.namespace.heading == 'Groups' or str(concept.id) in expand:
        concept.set_children()
        for child in concept.children:
            _attach_attributes(child, langcode, expand)


def redirect_old_urls(request, view_name):
    langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
    old_new_views = {'index_html': 'themes', 'groups': 'groups'}
    view = old_new_views.get(view_name)
    if not view:
        raise Http404()
    return redirect(view, langcode=langcode)


def themes(request, langcode='en'):
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
        supergroup.set_attribute('prefLabel', langcode)
        supergroup.set_children()
        for concept in supergroup.children:
            concept.set_attribute('prefLabel', langcode)

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

    concept.set_children()
    concept.set_broader()

    for cp in concept.children + concept.broader_concepts:
        cp.set_attribute('prefLabel', langcode)

    concept.url = request.build_absolute_uri(
        reverse('concept_redirect', args=[concept.code]))

    return render(request, 'concept.html', {
        'languages': languages,
        'langcode': langcode,
        'concept': concept,
    })


def concept_redirect(request, concept_code):
    cp = get_object_or_404(
        Concept,
        code=concept_code,
        namespace__heading='Concepts',
    )
    return redirect('concept', langcode=DEFAULT_LANGCODE, concept_id=cp.id)


def relations(request, group_id, langcode):
    languages = Language.objects.values_list('code', flat=True)

    expand_text = request.GET.get('exp')
    expand = expand_text.split('-') if expand_text else []

    group = get_object_or_404(Concept, pk=group_id)
    _attach_attributes(group, langcode, expand)

    return render(request, 'relations.html', {
        'languages': languages,
        'langcode': langcode,
        'group': group,
        'get_params': request.GET.urlencode(),
    })


def theme_concepts(request, theme_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    letters = unicode_character_map.get(langcode, [])

    theme = get_object_or_404(Concept, pk=theme_id)
    theme.set_attribute('prefLabel', langcode)
    theme.set_children()

    for concept in theme.children:
        concept.set_attribute('prefLabel', langcode)

    try:
        letter_index = int(request.GET.get('letter', '0'))
    except ValueError:
        raise Http404

    if letter_index == 0:
        concepts = theme.children
    elif 0 < letter_index <= len(letters):
        concepts = [c for c in theme.children if c.prefLabel
                    and c.prefLabel[0] in letters[letter_index - 1]]
    elif letter_index == 99:
        concepts = [c for c in theme.children if c.prefLabel and
                    c.prefLabel[0] not in list(chain.from_iterable(letters))]
    else:
        raise Http404

    paginator = Paginator(concepts, NR_CONCEPTS_ON_PAGE)
    page = request.GET.get('page')
    try:
        concepts = paginator.page(page)
    except PageNotAnInteger:
        concepts = paginator.page(1)
    except EmptyPage:
        concepts = paginator.page(paginator.num_pages)

    return render(request, 'theme_concepts.html', {
        'languages': languages,
        'langcode': langcode,
        'theme': theme,
        'concepts': concepts,
        'letters': [l[0] for l in letters],
        'letter': letter_index,
        'get_params': request.GET.urlencode(),
    })

def alphabetic(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    letters = unicode_character_map.get(langcode, [])

    concepts = Concept.objects.filter(namespace__heading='Concepts')
    for concept in concepts:
        concept.set_attribute('prefLabel', langcode)
    concepts = sorted(concepts, key=lambda t: t.prefLabel)

    try:
        letter_index = int(request.GET.get('letter', '0'))
    except ValueError:
        raise Http404

    if letter_index == 0:
        pass
    elif 0 < letter_index <= len(letters):
        concepts = [c for c in concepts if c.prefLabel[0] in
                    letters[letter_index - 1]]
    elif letter_index == 99:
        concepts = [c for c in concepts if c.prefLabel[0] not in
                    list(chain.from_iterable(letters))]
    else:
        raise Http404

    paginator = Paginator(concepts, NR_CONCEPTS_ON_PAGE)
    page = request.GET.get('page')
    try:
        concepts = paginator.page(page)
    except PageNotAnInteger:
        concepts = paginator.page(1)
    except EmptyPage:
        concepts = paginator.page(paginator.num_pages)

    return render(request, 'alphabetic_listings.html', {
        'languages': languages,
        'langcode': langcode,
        'concepts': concepts,
        'letters': [l[0] for l in letters],
        'letter': letter_index,
        'get_params': request.GET.urlencode(),
    })
