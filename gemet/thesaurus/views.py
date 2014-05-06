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
    Property,
)
from collation_charts import unicode_character_map
from forms import SearchForm


NR_CONCEPTS_ON_PAGE = 20
DEFAULT_LANGCODE = 'en'


def _attach_attributes(concept, langcode, expand=[]):
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

    concept = get_object_or_404(Term, pk=concept_id)

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
        reverse('concept_redirect', kwargs={'concept_type': 'concept',
                                            'concept_code': concept.code}))

    return render(request, 'concept.html', {
        'languages': languages,
        'language': language,
        'concept': concept,
    })


def concept_redirect(request, concept_type, concept_code):
    concept_types = {
        'concept': Term,
        'theme': Theme,
        'group': Group,
        'supergroup': SuperGroup
    }
    model = concept_types.get(concept_type)
    if model:
        cp = get_object_or_404(model, code=concept_code)
        return redirect(concept_type, langcode=DEFAULT_LANGCODE,
                        concept_id=cp.id)
    else:
        raise Http404


def theme(request, concept_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    theme = get_object_or_404(Theme, pk=concept_id)

    for property_name in ['prefLabel', 'definition', 'scopeNote']:
        theme.set_attribute(property_name, langcode)

    theme.translations = theme.properties.filter(name='prefLabel')
    theme.set_children()

    for tp in theme.children:
        tp.set_attribute('prefLabel', langcode)

    theme.children = sorted([c for c in theme.children if c.prefLabel],
                            key=lambda t: t.prefLabel.lower())
    theme.translations = sorted([c for c in theme.translations
                                 if c.language.name],
                                key=lambda t: t.language.name.lower())

    theme.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'theme',
                                            'concept_code': theme.code}))

    return render(request, 'theme.html', {
        'languages': languages,
        'language': language,
        'theme': theme,
    })


def group(request, concept_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    group = get_object_or_404(Group, pk=concept_id)

    for property_name in ['prefLabel', 'definition', 'scopeNote']:
        group.set_attribute(property_name, langcode)

    group.translations = group.properties.filter(name='prefLabel')

    group.set_broader()
    group_concepts = [r.target for r in group.source_relations
                      .filter(property_type__name='groupMember')
                      .prefetch_related('target')]

    for gp in group.broader_concepts + group_concepts:
        gp.set_attribute('prefLabel', langcode)

    group.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'group',
                                            'concept_code': group.code}))

    return render(request, 'group.html', {
        'languages': languages,
        'language': language,
        'group': group,
        'group_concepts': group_concepts,
    })


def supergroup(request, concept_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    supergroup = get_object_or_404(SuperGroup, pk=concept_id)

    for property_name in ['prefLabel', 'definition', 'scopeNote']:
        supergroup.set_attribute(property_name, langcode)

    supergroup.translations = supergroup.properties.filter(name='prefLabel')

    supergroup.set_children()

    for gp in supergroup.children:
        gp.set_attribute('prefLabel', langcode)

    supergroup.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'supergroup',
                                            'concept_code': supergroup.code}))

    return render(request, 'supergroup.html', {
        'languages': languages,
        'language': language,
        'supergroup': supergroup,
    })


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
    return False


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

    if concepts:
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


def search(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    concepts = []
    query = ''

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            concepts = [
                (p.concept, p.value) for p in
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
                    order_by=['value_coll']
                )
                .prefetch_related('concept')
            ]
            for concept, concept_name in concepts:
                concept.name = concept_name
                concept.broader_context = '; '.join([
                    r.target.get_property_value('prefLabel', langcode)
                    for r in concept.source_relations
                    .filter(property_type__name='broader')
                    .prefetch_related('target')])
    else:
        form = SearchForm(
            initial={'langcode': langcode}
        )

    return render(request, 'search.html', {
        'languages': languages,
        'language': language,
        'form': form,
        'concepts': [c[0] for c in concepts],
        'query': query,
    })
