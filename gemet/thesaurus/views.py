from itertools import chain
from collections import OrderedDict

from django.http import Http404
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from gemet.thesaurus.models import (
    Language,
    Theme,
    Namespace,
    SuperGroup,
    Term,
    Group,
    Property,
    DefinitionSource,
    Relation,
)
from gemet.thesaurus.collation_charts import unicode_character_map
from gemet.thesaurus.forms import SearchForm, ExportForm
from gemet.thesaurus.utils import search_queryset, exp_decrypt
from gemet.thesaurus import DEFAULT_LANGCODE, NR_CONCEPTS_ON_PAGE


class LanguageMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.langcode = kwargs.pop("langcode", DEFAULT_LANGCODE)
        self.language = get_object_or_404(Language, pk=self.langcode)
        return super(LanguageMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LanguageMixin, self).get_context_data(**kwargs)
        context.update({"language": self.language,
                        "languages": Language.objects.values_list('code',
                                                                  flat=True)})
        return context


class AboutView(LanguageMixin, TemplateView):
    template_name = "about.html"


class ChangesView(LanguageMixin, TemplateView):
    template_name = "changes.html"


class ThemesView(LanguageMixin, TemplateView):
    template_name = "themes.html"

    def get_context_data(self, **kwargs):
        context = super(ThemesView, self).get_context_data(**kwargs)

        themes = (
            Property.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                concept_id__in=Theme.objects.values_list('id', flat=True)
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

        context.update({"themes": themes})
        return context


class GroupsView(LanguageMixin, TemplateView):
    template_name = "groups.html"

    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data(**kwargs)

        supergroups = (
            Property.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                concept_id__in=SuperGroup.objects.values_list('id', flat=True)
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

        context.update({"supergroups": supergroups})
        return context


class DefinitionSourcesView(LanguageMixin, TemplateView):
    template_name = "definition_sources.html"

    def get_context_data(self, **kwargs):
        context = super(DefinitionSourcesView, self).get_context_data(**kwargs)

        definitions = DefinitionSource.objects.all()

        context.update({"definitions": definitions})
        return context


class AlphabetsView(LanguageMixin, TemplateView):
    template_name = "alphabets.html"

    def get_context_data(self, **kwargs):
        context = super(AlphabetsView, self).get_context_data(**kwargs)

        letters = unicode_character_map.get(self.langcode, [])

        context.update({"letters": letters})
        return context


class SearchView(LanguageMixin, FormView):
    template_name = "search.html"
    form_class = SearchForm

    query = ''
    concepts = []

    def get_initial(self):
        return {'langcode': self.langcode}

    def get_success_url(self):
        return reverse('search', kwargs={'langcode': self.langcode})

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        context.update({"query": self.query, "concepts": self.concepts})
        return context

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        self.concepts = search_queryset(
            self.query,
            self.language
        )

        return self.render_to_response(self.get_context_data(form=form))


class RelationsView(LanguageMixin, TemplateView):
    template_name = "relations.html"

    def dispatch(self, request, *args, **kwargs):
        self.group_id = kwargs.pop("group_id")
        return super(RelationsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        expand_text = self.request.GET.get('exp')
        if expand_text:
            expand_text = expand_text.replace(' ', '+')
            expand_text = exp_decrypt(expand_text)
            expand_list = expand_text.split('-')
        else:
            expand_list = []

        group = get_object_or_404(Group, pk=self.group_id)
        group.set_attributes(self.langcode, ['prefLabel'])
        context = super(RelationsView, self).get_context_data(**kwargs)
        context.update({
            'group_id': self.group_id,
            'group': group,
            'get_params': self.request.GET.urlencode(),
            'expand_list': expand_list,
        })
        return context


class ConceptView(LanguageMixin, DetailView):

    def dispatch(self, request, *args, **kwargs):
        self.concept_id = kwargs.pop('concept_id')
        return super(ConceptView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        concept = get_object_or_404(self.model, pk=self.concept_id)
        concept.set_siblings(self.langcode)
        concept.set_parents(self.langcode)
        concept.translations = (
            concept.properties
            .filter(name='prefLabel')
            .order_by('language__name')
        )
        concept.set_attributes(self.langcode,
                               ['prefLabel', 'definition', 'scopeNote'])
        concept.url = self.request.build_absolute_uri(
            reverse('concept_redirect', kwargs={
                'concept_type': self.concept_type,
                'concept_code': concept.code
            }))

        return concept

    def get_context_data(self, **kwargs):
        context = super(ConceptView, self).get_context_data(**kwargs)

        languages = [
            p.language.code
            for p in context[self.context_object_name].properties.filter(
                name='prefLabel',
                value__isnull=False,
            )]

        context.update({"languages": languages})
        return context


class TermView(ConceptView):
    template_name = "concept.html"
    model = Term
    concept_type = 'concept'
    context_object_name = 'concept'


class ThemeView(ConceptView):
    template_name = "theme.html"
    model = Theme
    concept_type = 'theme'
    context_object_name = 'theme'


class GroupView(ConceptView):
    template_name = "group.html"
    model = Group
    concept_type = 'group'
    context_object_name = 'group'


class SuperGroupView(ConceptView):
    template_name = "supergroup.html"
    model = SuperGroup
    concept_type = 'supergroup'
    context_object_name = 'supergroup'


class PaginatorView(LanguageMixin, ListView):
    context_object_name = 'concepts'
    paginate_by = NR_CONCEPTS_ON_PAGE

    def _filter_by_letter(self, properties, letters, startswith=True):
        if letters:
            q_queries = [Q(value__startswith=letter) for letter in letters]
            query = q_queries.pop()
            for q_query in q_queries:
                query |= q_query
            properties = properties.filter(query) if startswith \
                else properties.exclude(query)

        return properties

    def _get_letters_presence(self, all_letters, theme=None):
        letters = (
            Property.objects
            .filter(
                name='prefLabel',
                language_id=self.langcode,
            )
            .extra(
                select={'first_letter': 'SUBSTR(value, 1, 1)'}
            )
        )
        if theme:
            letters = letters.filter(
                concept_id__in=(
                    theme.source_relations
                    .filter(property_type__name='themeMember')
                    .values_list('target_id', flat=True)
                )
            )
        unique_letters = set(letters.values_list('first_letter', flat=True))

        return [
            (letter_group[0], bool(set(letter_group) & unique_letters))
            for letter_group in all_letters]

    def get_queryset(self, theme=None):
        try:
            self.letter_index = int(self.request.GET.get('letter', '0'))
        except ValueError:
            raise Http404

        all_letters = unicode_character_map.get(self.langcode, [])

        startswith = True
        if self.letter_index == 0:
            letters = []
        elif 0 < self.letter_index <= len(all_letters):
            letters = all_letters[self.letter_index - 1]
        elif self.letter_index == 99:
            letters = list(chain.from_iterable(all_letters))
            startswith = False
        else:
            raise Http404

        self.letters = self._get_letters_presence(all_letters, theme)

        all_concepts = self._filter_by_letter(self.concepts, letters,
                                              startswith)

        return all_concepts

    def get_context_data(self, **kwargs):
        context = super(PaginatorView, self).get_context_data(**kwargs)
        page_number = context['page_obj'].number
        total_pages = len(context['page_obj'].paginator.page_range)
        distance_number = 9

        context.update({
            'letters': self.letters,
            'letter': self.letter_index,
            'get_params': self.request.GET.urlencode(),
            'visible_pages': range(
                max(1, page_number - distance_number),
                min(page_number + distance_number + 1, total_pages + 1)
            ),
        })

        return context


class ThemeConceptsView(PaginatorView):
    template_name = "theme_concepts.html"
    model = Theme

    def dispatch(self, request, *args, **kwargs):
        self.theme_id = kwargs.pop('theme_id')
        return super(ThemeConceptsView, self).dispatch(request, *args,
                                                       **kwargs)

    def get_queryset(self):
        self.theme = get_object_or_404(self.model, pk=self.theme_id)
        self.theme.set_attributes(self.langcode, ['prefLabel'])
        self.concepts = self.theme.get_children(self.langcode)
        return super(ThemeConceptsView, self).get_queryset(self.theme)

    def get_context_data(self, **kwargs):
        context = super(ThemeConceptsView, self).get_context_data(**kwargs)
        context.update({'theme': self.theme})

        return context


class AlphabeticView(PaginatorView):
    template_name = "alphabetic_listings.html"
    model = Property

    def get_queryset(self):
        self.concepts = (
            self.model.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                concept__namespace__heading='Concepts'
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

        return super(AlphabeticView, self).get_queryset()


class BackboneView(TemplateView):
    template_name = 'downloads/backbone.html'

    def get_context_data(self, **kwargs):
        context = super(BackboneView, self).get_context_data(**kwargs)

        relations = (
            Relation.objects.filter(
                property_type__label__in=['Theme', 'Group'],
            ).values(
                'source__code', 'property_type__label', 'target__code',
            )
        )

        context.update({"relations": relations})
        return context


class XMLTemplateView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context,
                                       content_type="text/xml; charset=utf-8")


class BackboneRDFView(XMLTemplateView):
    template_name = 'downloads/backbone.rdf'

    def get_context_data(self, **kwargs):
        context = super(BackboneRDFView, self).get_context_data(**kwargs)

        supergroup_uri = Namespace.objects.get(heading='Super groups').type_url
        supergroups = SuperGroup.objects.values('code')

        group_uri = Namespace.objects.get(heading='Groups').type_url
        groups = Group.objects.values('code')

        theme_uri = Namespace.objects.get(heading='Themes').type_url
        themes = Theme.objects.values('code')

        relations = {}
        concepts = Term.objects.values('id', 'code')

        for concept in concepts:
            relations.update({
                concept['code']: (Relation.objects
                                  .filter(source_id=concept['id'],
                                          property_type__name__in=
                                          ['theme', 'group'],
                                          )
                                  .values('target__code',
                                          'property_type__name',
                                          )
                                  )
            })

        context.update({
            'supergroup_uri': supergroup_uri,
            'supergroups': supergroups,
            'group_uri': group_uri,
            'groups': groups,
            'theme_uri': theme_uri,
            'themes': themes,
            'concept_relations': relations,
        })
        return context


class DefinitionsView(TemplateView):
    template_name = 'downloads/definitions.html'

    def get_context_data(self, **kwargs):
        context = super(DefinitionsView, self).get_context_data(**kwargs)

        concepts = []
        for term in Term.objects.all():
            concept_properties = (
                term.properties
                .filter(
                    language__code=DEFAULT_LANGCODE,
                    name__in=['prefLabel', 'scopeNote', 'definition',
                              'notation'],
                    )
                .values('name', 'value')
                )
            if concept_properties:
                concept = {'code': term.code}
                for c in concept_properties:
                    concept.update({c['name']: c['value']})
                concepts.append(concept)

        context.update({"concepts": concepts})

        return context


class GemetGroupsView(TemplateView):
    template_name = 'downloads/gemet-groups.html'
    translate = {
        'Super groups': 'SuperGroup',
        'Groups': 'Group',
        'Themes': 'Theme',
    }

    def get_context_data(self, **kwargs):
        context = super(GemetGroupsView, self).get_context_data(**kwargs)

        supergroups = (
            Property.objects
            .filter(
                name='prefLabel',
                concept__namespace__heading='Super groups',
                language__code=DEFAULT_LANGCODE,
            )
            .values('concept__code', 'value')
        )

        relations = (
            Relation.objects
            .filter(
                target_id__in=SuperGroup.objects.values_list('id', flat=True),
                property_type__label='broader term',
            )
            .values('target__code', 'source_id')
        )

        groups = []
        for relation in relations:
            source = (
                Property.objects
                .filter(
                    concept_id=relation['source_id'],
                    name='prefLabel',
                    language__code=DEFAULT_LANGCODE,
                )
                .values('concept__code', 'value')
                .first()
            )
            groups.append({
                'source_code': source['concept__code'],
                'source_label': source['value'],
                'target_code': relation['target__code'],
            })

        themes = (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=DEFAULT_LANGCODE,
                concept__namespace__heading='Themes',
            )
            .values('concept__code', 'value')
        )

        context.update({
            'supergroups': supergroups,
            'supergroup_type': self.translate.get('Super groups'),
            'groups': groups,
            'group_type': self.translate.get('Groups'),
            'themes': themes,
            'theme_type': self.translate.get('Themes'),
        })

        return context


class GemetRelationsMixin(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(GemetRelationsMixin, self).get_context_data(**kwargs)

        self.relations = Relation.objects.filter(
            source__namespace__heading='Concepts',
            target__namespace__heading='Concepts',
        ).values(
            'source__code',
            'target__code',
            'property_type__label',
        )

        return context


class GemetRelationsView(GemetRelationsMixin):
    template_name = 'downloads/gemet-relations.html'
    translate = {
        'narrower term': 'Narrower',
        'broader term': 'Broader',
        'related': 'Related',
        'relatedMatch': 'Relatedmatch',
        'exactMatch': 'Exactmatch',
        'closeMatch': 'Closematch',
        'narrowMatch': 'Narrowmatch',
        'broadMatch': 'BroadMatch',
    }

    def get_context_data(self, **kwargs):
        context = super(GemetRelationsView, self).get_context_data(**kwargs)

        for r in self.relations:
            r['property_type__label'] = self.translate[
                r['property_type__label']
            ]
        context.update({'relations': self.relations})

        return context


class Skoscore(GemetRelationsMixin, XMLTemplateView):
    template_name = 'downloads/skoscore.rdf'

    def get_context_data(self, **kwargs):
        context = super(Skoscore, self).get_context_data(**kwargs)

        relations = {}
        for r in self.relations:
            label = r['property_type__label']
            target_code = r['target__code']
            d = {
                'target__code':
                ('' if 'Matc' in label else 'concept/') + target_code,
                'property_type__label': label.split(' ')[0]
            }
            source_code = r['source__code']
            if source_code in relations:
                relations[source_code].append(d)
            else:
                relations[source_code] = [d]
        context.update({'concept_relations': relations})

        return context


class DefinitionsByLanguage(LanguageMixin, XMLTemplateView):
    template_name = 'downloads/language_definitions.rdf'

    def get_context_data(self, **kwargs):
        context = super(DefinitionsByLanguage, self).get_context_data(**kwargs)

        concepts = Term.objects.values('id', 'code').order_by('code')
        definitions = OrderedDict()

        for concept in concepts:
            properties = sorted(
                (
                    Property.objects
                    .filter(
                        concept_id=concept['id'],
                        language=self.language,
                        name__in=['definition', 'prefLabel'],
                    )
                    .values('name', 'value')
                ),
                key=lambda x: x['name'],
                reverse=True
            )
            definitions[concept['code']] = properties

        context.update({'definitions': definitions})
        return context


class GroupsByLanguage(LanguageMixin, XMLTemplateView):
    template_name = 'downloads/language_groups.rdf'

    def get_context_data(self, **kwargs):
        context = super(GroupsByLanguage, self).get_context_data(**kwargs)

        for heading in ['Super groups', 'Groups', 'Themes']:
            context.update({
                heading.replace(' ', '_'): (
                    Property.objects
                    .filter(
                        concept__namespace__heading=heading,
                        language=self.language,
                        name='prefLabel',
                    )
                    .values(
                        'concept__code',
                        'value',
                    )
                )
            })

        return context


class GemetThesaurus(XMLTemplateView):
    template_name = 'downloads/gemetThesaurus.xml'


class DownloadView(LanguageMixin, FormView):
    template_name = "downloads/download.html"
    form_class = ExportForm

    def get_initial(self):
        return {'language_names': self.language}

    def form_valid(self, form):
        if self.request.POST['type'] == 'definitions':
            reverse_name = 'language_definitions'
        elif self.request.POST['type'] == 'groups':
            reverse_name = 'language_groups'
        else:
            raise Http404

        langcode = form.cleaned_data['language_names'].code
        return redirect(reverse_name, langcode=langcode)


def redirect_old_urls(request, view_name):
    langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
    old_new_views = {
        'index_html': 'themes',
        'groups': 'groups',
        'rdf': 'download',
    }
    view = old_new_views.get(view_name, view_name)
    if view in ['themes', 'groups', 'download', 'gemet-definitions.rdf',
                'gemet-groups.rdf']:
        return redirect(view, permanent=True, langcode=langcode)
    else:
        return redirect(view, permanent=True)


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


def error404(request):
    language = Language.objects.get(pk=DEFAULT_LANGCODE)
    return render(request, '404.html', {'language': language})
