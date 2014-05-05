from itertools import chain

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from gemet.thesaurus.models import (
    Language,
    Concept,
    Theme,
    SuperGroup,
    Term,
    Group,
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
    language = get_object_or_404(Language, pk=langcode)

    themes = Theme.objects.all()
    for theme in themes:
        theme.set_attribute('prefLabel', langcode)

    themes = sorted(themes, key=lambda t: t.prefLabel.lower())

    return render(request, 'themes.html', {
        'languages': languages,
        'language': language,
        'themes': themes,
    })


def groups(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    supergroups = SuperGroup.objects.all()

    for supergroup in supergroups:
        supergroup.set_attribute('prefLabel', langcode)
        supergroup.set_children()
        for concept in supergroup.children:
            concept.set_attribute('prefLabel', langcode)

    return render(request, 'groups.html', {
        'languages': languages,
        'language': language,
        'supergroups': supergroups,
    })


def concept(request, concept_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

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
        'language': language,
        'concept': concept,
    })


def concept_redirect(request, concept_code):
    cp = get_object_or_404(Term, code=concept_code)
    return redirect('concept', langcode=DEFAULT_LANGCODE, concept_id=cp.id)


def relations(request, group_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    expand_text = request.GET.get('exp')
    expand = expand_text.split('-') if expand_text else []

    group = get_object_or_404(Group, pk=group_id)
    _attach_attributes(group, langcode, expand)

    return render(request, 'relations.html', {
        'languages': languages,
        'language': language,
        'group': group,
        'get_params': request.GET.urlencode(),
    })


def _letter_exists(letter, all_concepts):
    for l in letter:
        for concept in all_concepts:
            if l == concept.prefLabel[0]:
                return True
    return None


def _get_concept_params(all_concepts, request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    letters = unicode_character_map.get(langcode, [])

    all_concepts = sorted([c for c in all_concepts if c.prefLabel],
                          key=lambda t: t.prefLabel.lower())

    try:
        letter_index = int(request.GET.get('letter', '0'))
    except ValueError:
        raise Http404

    if letter_index == 0:
        concepts = all_concepts
    elif 0 < letter_index <= len(letters):
        concepts = [c for c in all_concepts if c.prefLabel and
                    c.prefLabel[0] in letters[letter_index - 1]]
    elif letter_index == 99:
        concepts = [c for c in all_concepts if c.prefLabel and
                    c.prefLabel[0] not in list(chain.from_iterable(letters))]
    else:
        raise Http404

    if concepts != []:
        paginator = Paginator(concepts, NR_CONCEPTS_ON_PAGE)
        page = request.GET.get('page')
        try:
            concepts = paginator.page(page)
        except PageNotAnInteger:
            concepts = paginator.page(1)
        except EmptyPage:
            concepts = paginator.page(paginator.num_pages)

    return {
        'languages': languages,
        'language': language,
        'concepts': concepts,
        'letters': [(l[0], _letter_exists(l, all_concepts)) for l in letters],
        'letter': letter_index,
        'get_params': request.GET.urlencode()
    }


def theme_concepts(request, theme_id, langcode):
    theme = get_object_or_404(Theme, pk=theme_id)
    theme.set_attribute('prefLabel', langcode)
    theme.set_children()

    for concept in theme.children:
        concept.set_attribute('prefLabel', langcode)

    params = _get_concept_params(theme.children, request, langcode)
    params.update({'theme': theme})

    return render(request, 'theme_concepts.html', params)


def alphabetic(request, langcode):
    concepts = Term.objects.all()
    for concept in concepts:
        concept.set_attribute('prefLabel', langcode)

    return render(request, 'alphabetic_listings.html',
                  _get_concept_params(concepts, request, langcode))


def alphabets(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    letters = unicode_character_map.get(langcode, [])

    return render(request, 'alphabets.html', {
        'languages': languages,
        'language': language,
        'letters': letters
    })
