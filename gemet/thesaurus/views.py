from itertools import chain
from base64 import encodestring, decodestring
from zlib import compress, decompress

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from gemet.thesaurus.models import (
    Language,
    Theme,
    Namespace,
    SuperGroup,
    Term,
    Group,
    Property,
    DefinitionSource,
)
from collation_charts import unicode_character_map
from forms import SearchForm
from gemet.thesaurus import DEFAULT_LANGCODE, NR_CONCEPTS_ON_PAGE


def about(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)
    return render(request, 'about.html', {
        'languages': languages,
        'language': language
    })


def redirect_old_urls(request, view_name):
    langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
    old_new_views = {'index_html': 'themes', 'groups': 'groups'}
    view = old_new_views.get(view_name)
    if not view:
        raise Http404()
    return redirect(view, langcode=langcode)


def themes(request, langcode=DEFAULT_LANGCODE):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    themes = (
        Property.objects.filter(
            name='prefLabel',
            language__code=langcode,
            concept_id__in=Theme.objects.values_list('id', flat=True)
        )
        .extra(select={'name': 'value',
                       'id': 'concept_id'},
               order_by=['name'])
        .values('id', 'name')
    )

    return render(request, 'themes.html', {
        'languages': languages,
        'language': language,
        'themes': themes,
    })


def groups(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    supergroups = (
        Property.objects.filter(
            name='prefLabel',
            language__code=langcode,
            concept_id__in=SuperGroup.objects.values_list('id', flat=True)
        )
        .extra(select={'name': 'value',
                       'id': 'concept_id'},
               order_by=['name'])
        .values('id', 'name')
    )

    return render(request, 'groups.html', {
        'languages': languages,
        'language': language,
        'supergroups': supergroups,
    })


def concept(request, concept_id, langcode):
    concept = get_object_or_404(Term, pk=concept_id)
    language = get_object_or_404(Language, pk=langcode)
    languages = [p.language.code for p in concept.properties.filter(
        name='prefLabel',
        value__isnull=False)]

    concept.translations = concept.properties.filter(
        name='prefLabel'
        ).order_by(
        'language__name'
        )

    concept.set_attributes(langcode, ['prefLabel', 'definition', 'scopeNote'])

    for parent in ['group', 'theme']:
        concept.set_parent(langcode, parent)

    concept.set_siblings(langcode, 'broader')
    concept.set_siblings(langcode, 'narrower')
    concept.set_siblings(langcode, 'related')

    concept.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'concept',
                                            'concept_code': concept.code}))

    return render(request, 'concept.html', {
        'languages': languages,
        'language': language,
        'concept': concept,
    })


def theme(request, concept_id, langcode):
    theme = get_object_or_404(Theme, pk=concept_id)
    language = get_object_or_404(Language, pk=langcode)
    languages = [p.language.code for p in theme.properties.filter(
        name='prefLabel',
        value__isnull=False)]

    theme.translations = theme.properties.filter(
        name='prefLabel'
        ).order_by(
        'language__name'
        )

    theme.set_attributes(langcode, ['prefLabel', 'definition', 'scopeNote'])

    theme.set_siblings(langcode, 'themeMember')
    theme.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'theme',
                                            'concept_code': theme.code}))

    return render(request, 'theme.html', {
        'languages': languages,
        'language': language,
        'theme': theme,
    })


def group(request, concept_id, langcode):
    group = get_object_or_404(Group, pk=concept_id)
    language = get_object_or_404(Language, pk=langcode)
    languages = [p.language.code for p in group.properties.filter(
        name='prefLabel',
        value__isnull=False)]

    group.translations = group.properties.filter(
        name='prefLabel'
        ).order_by(
        'language__name'
        )

    group.set_attributes(langcode, ['prefLabel', 'definition', 'scopeNote'])
    group.set_siblings(langcode, 'broader')
    group.set_siblings(langcode, 'groupMember')
    group.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'group',
                                            'concept_code': group.code}))

    return render(request, 'group.html', {
        'languages': languages,
        'language': language,
        'group': group,
    })


def supergroup(request, concept_id, langcode):
    supergroup = get_object_or_404(SuperGroup, pk=concept_id)
    language = get_object_or_404(Language, pk=langcode)
    languages = [p.language.code for p in supergroup.properties.filter(
        name='prefLabel',
        value__isnull=False)]

    supergroup.translations = supergroup.properties.filter(
        name='prefLabel'
        ).order_by(
        'language__name'
        )

    supergroup.set_attributes(langcode,
                              ['prefLabel', 'definition', 'scopeNote'])
    supergroup.set_siblings(langcode, 'narrower')

    supergroup.url = request.build_absolute_uri(
        reverse('concept_redirect', kwargs={'concept_type': 'supergroup',
                                            'concept_code': supergroup.code}))

    return render(request, 'supergroup.html', {
        'languages': languages,
        'language': language,
        'supergroup': supergroup,
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


def exp_encrypt(exp):
    return encodestring(compress(exp))


def exp_decrypt(exp):
    return decompress(decodestring(exp))


def relations(request, group_id, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    expand_text = request.GET.get('exp')
    if expand_text:
        expand_text = expand_text.replace(' ', '+')
        expand_text = exp_decrypt(expand_text)
        expand_list = expand_text.split('-')
    else:
        expand_list = []

    group = get_object_or_404(Group, pk=group_id)
    group.set_attributes(langcode, ['prefLabel'])

    return render(request, 'relations.html', {
        'languages': languages,
        'language': language,
        'group': group,
        'group_id': group.id,
        'get_params': request.GET.urlencode(),
        'expand_list': expand_list,
    })


def _filter_by_letter(properties, letters, startswith=True):
    if letters:
        q_queries = [Q(value__startswith=letter) for letter in letters]
        query = q_queries.pop()
        for q_query in q_queries:
            query |= q_query
        properties = properties.filter(query) if startswith \
            else properties.exclude(query)
    return properties


def _letter_exists(all_concepts, letters):
    return _filter_by_letter(all_concepts, letters).count()


def _get_concept_params(all_concepts, request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    try:
        letter_index = int(request.GET.get('letter', '0'))
    except ValueError:
        raise Http404

    all_letters = unicode_character_map.get(langcode, [])

    startswith = True
    if letter_index == 0:
        letters = []
    elif 0 < letter_index <= len(all_letters):
        letters = all_letters[letter_index - 1]
    elif letter_index == 99:
        letters = list(chain.from_iterable(all_letters))
        startswith = False
    else:
        raise Http404

    all_concepts = _filter_by_letter(all_concepts, letters, startswith)

    paginator = Paginator(all_concepts, NR_CONCEPTS_ON_PAGE)
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
        'letters':
        [(l[0], _letter_exists(all_concepts, l)) for l in all_letters],
        'letter': letter_index,
        'get_params': request.GET.urlencode()
    }


def theme_concepts(request, theme_id, langcode):
    theme = get_object_or_404(Theme, pk=theme_id)
    theme.set_attributes(langcode, ['prefLabel'])
    params = _get_concept_params(theme.get_children(langcode), request,
                                 langcode)
    params.update({'theme': theme})

    return render(request, 'theme_concepts.html', params)


def alphabetic(request, langcode):
    concepts = (
        Property.objects.filter(
            name='prefLabel',
            language__code=langcode,
        )
        .extra(select={'name': 'value',
                       'id': 'concept_id'},
               order_by=['name'])
        .values('id', 'name')
    )

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
            concepts = (
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
    else:
        form = SearchForm(
            initial={'langcode': langcode}
        )

    return render(request, 'search.html', {
        'languages': languages,
        'language': language,
        'form': form,
        'concepts': concepts,
        'query': query,
    })


def old_concept_redirect(request):
    langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
    ns = request.GET.get('ns')
    cp = request.GET.get('cp')
    if ns and cp:
        views_map = {
            'Concepts': 'concept',
            'Themes': 'theme',
            'Groups': 'group',
            'Super groups': 'supergroup'
        }
        concept_types = {
            '1': Term,
            '2': SuperGroup,
            '3': Group,
            '4': Theme
        }
        concept_type = concept_types.get(ns)
        if concept_type:
            namespace = get_object_or_404(Namespace, id=ns)
            concept = get_object_or_404(concept_type, namespace=namespace,
                                        code=cp)
            get_object_or_404(Language, pk=langcode)
            return redirect(views_map.get(namespace.heading),
                            langcode=langcode,
                            concept_id=concept.id)
        else:
            raise Http404
    else:
        raise Http404


def definition_sources(request, langcode):
    languages = Language.objects.values_list('code', flat=True)
    language = get_object_or_404(Language, pk=langcode)

    definitions = DefinitionSource.objects.all()

    return render(request, 'definition_sources.html', {
        'languages': languages,
        'language': language,
        'definitions': definitions,
    })


def error404(request):
    language = Language.objects.get(pk=DEFAULT_LANGCODE)
    return render(request, '404.html', {'language': language})
