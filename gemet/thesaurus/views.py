from itertools import chain
from collections import OrderedDict
import sys
from xmlrpclib import Fault
from urllib import urlencode

from django.http import Http404, StreamingHttpResponse
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
from django.conf import settings

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
    InspireTheme,
    ForeignRelation,
    Concept,
)
from gemet.thesaurus.collation_charts import unicode_character_map
from gemet.thesaurus.forms import SearchForm, ExportForm
from gemet.thesaurus.utils import search_queryset, exp_decrypt, is_rdf
from gemet.thesaurus import (
    DEFAULT_LANGCODE,
    NR_CONCEPTS_ON_PAGE,
    NS_ID_VIEW_MAPPING,
)


class HeaderMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.langcode = kwargs.pop("langcode", DEFAULT_LANGCODE)
        self.language = get_object_or_404(Language, pk=self.langcode)
        return super(HeaderMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HeaderMixin, self).get_context_data(**kwargs)
        context.update({
            'language': self.language,
            'languages': (
                Language.objects
                .values('code', 'name')
                .order_by('name')
            ),
            'search_form': SearchForm(),
        })
        return context


class AboutView(HeaderMixin, TemplateView):
    template_name = "about.html"


class ChangesView(HeaderMixin, TemplateView):
    template_name = "changes.html"


class WebServicesView(HeaderMixin, TemplateView):
    template_name = 'webservices.html'


class ThemesView(HeaderMixin, TemplateView):
    template_name = "themes.html"
    model_cls = Theme
    page_title = 'Themes'
    theme_url = 'theme_concepts'
    view_name = 'themes'
    css_class = 'split-20'

    def _get_themes_by_langcode(self, langcode):
        return (
            Property.objects.filter(
                name='prefLabel',
                language__code=langcode,
                concept_id__in=self.model_cls.objects.values_list(
                    'id', flat=True)
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name', 'concept__code')
        )

    def get_context_data(self, **kwargs):
        context = super(ThemesView, self).get_context_data(**kwargs)

        themes = self._get_themes_by_langcode(self.langcode)
        if not themes:
            themes = self._get_themes_by_langcode(DEFAULT_LANGCODE)
            context.update({'language_warning': True})

        context.update({
            'themes': themes,
            'page_title': self.page_title,
            'theme_url': self.theme_url,
            'view_name': self.view_name,
            'ns_version': self.model_cls.objects.get_ns().version,
            'css_class': self.css_class,
        })
        return context


class InspireThemesView(ThemesView):
    model_cls = InspireTheme
    page_title = 'INSPIRE Spatial Data Themes'
    theme_url = 'inspire_theme'
    view_name = 'inspire_themes'
    css_class = 'split-17'

    def get_context_data(self, **kwargs):
        context = super(InspireThemesView, self).get_context_data(**kwargs)
        languages = [lang for lang in context['languages'] if
                     Property.objects.filter(
                         language_id=lang.get('code'),
                         concept__namespace=self.model_cls.objects.get_ns(),
                     )]

        context.update({'languages': languages})
        return context


class GroupsView(HeaderMixin, TemplateView):
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

        context.update({
            "supergroups": supergroups,
            "ns_version": Group.objects.get_ns().version
        })
        return context


class DefinitionSourcesView(HeaderMixin, TemplateView):
    template_name = "definition_sources.html"

    def get_context_data(self, **kwargs):
        context = super(DefinitionSourcesView, self).get_context_data(**kwargs)

        definitions = DefinitionSource.objects.all()

        context.update({"definitions": definitions})
        return context


class AlphabetsView(HeaderMixin, TemplateView):
    template_name = "alphabets.html"

    def get_context_data(self, **kwargs):
        context = super(AlphabetsView, self).get_context_data(**kwargs)

        letters = unicode_character_map.get(self.langcode, [])
        context.update({"letters": letters})
        return context


class SearchView(HeaderMixin, FormView):
    template_name = "search.html"
    form_class = SearchForm

    query = ''
    concepts = []

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        context.update({
            "query": self.query,
            "concepts": self.concepts,
            "ns_version": Term.objects.get_ns().version
        })
        return context

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        self.concepts = search_queryset(
            self.query,
            self.language
        )

        return self.render_to_response(self.get_context_data(form=form))


class RelationsView(HeaderMixin, TemplateView):
    template_name = "relations.html"

    def get_context_data(self, **kwargs):
        code = self.kwargs.get('group_code')
        group = get_object_or_404(Group, code=code)
        group.set_attributes(self.langcode, ['prefLabel'])

        expand_text = self.request.GET.get('exp')
        if expand_text:
            expand_text = expand_text.replace(' ', '+')
            expand_text = exp_decrypt(expand_text)
            expand_list = expand_text.split('-')
        else:
            expand_list = []

        context = super(RelationsView, self).get_context_data(**kwargs)
        context.update({
            'group_id': group.id,
            'group': group,
            'expand_list': expand_list,
            'get_params': self.request.GET.urlencode(),
            'ns_version': Term.objects.get_ns().version
        })
        return context


class ConceptView(HeaderMixin, DetailView):

    def get_object(self):
        code = self.kwargs.get('code')
        concept = get_object_or_404(self.model, code=code)
        concept.set_siblings(self.langcode)
        concept.set_parents(self.langcode)
        concept.translations = (
            concept.properties
            .filter(name='prefLabel')
            .order_by('language__name')
        )
        concept.set_attributes(self.langcode,
                               ['prefLabel', 'definition', 'scopeNote'])
        concept.url = self.request.build_absolute_uri(concept.get_about_url())

        return concept

    def get_context_data(self, **kwargs):
        context = super(ConceptView, self).get_context_data(**kwargs)

        languages = [{
            'code': p.language.code,
            'name': p.language.name,
        }
            for p in context[self.context_object_name].properties.filter(
                name='prefLabel',
                value__isnull=False,
            )]

        context.update({
            "languages": languages,
            "ns_version": self.model.objects.get_ns().version
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if is_rdf(request):
            return render_rdf(self.request, self.object)
        return self.render_to_response(context)


class TermView(ConceptView):
    template_name = "concept.html"
    model = Term
    concept_type = 'concept'
    context_object_name = 'concept'

    def get_object(self):
        term = super(TermView, self).get_object()
        term.set_attributes(self.langcode, ['source', 'altLabel'])
        if not hasattr(term, 'definition'):
            term.set_attributes(DEFAULT_LANGCODE, ['definition'])
            term.default_definition = True
        return term


class InspireThemeView(ConceptView):
    template_name = "inspire_theme.html"
    model = InspireTheme
    concept_type = 'inspire_theme'
    context_object_name = 'inspire_theme'


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


class PaginatorView(HeaderMixin, ListView):
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
            'visible_pages': range(
                max(1, page_number - distance_number),
                min(page_number + distance_number + 1, total_pages + 1)
            ),
        })

        return context


class ThemeConceptsView(PaginatorView):

    template_name = "theme_concepts.html"
    model = Theme

    def get_queryset(self):
        code = self.kwargs.get('theme_code')
        self.theme = get_object_or_404(self.model, code=code)
        self.theme.set_attributes(self.langcode, ['prefLabel'])
        self.concepts = self.theme.get_children(self.langcode)
        return super(ThemeConceptsView, self).get_queryset(self.theme)

    def get_context_data(self, **kwargs):
        context = super(ThemeConceptsView, self).get_context_data(**kwargs)
        if not hasattr(self.theme, 'prefLabel'):
            self.theme.set_attributes(DEFAULT_LANGCODE, ['prefLabel'])
            context.update({'language_warning': True})
        context.update({
            'theme': self.theme,
            'ns_version': Term.objects.get_ns().version
        })

        return context


class AlphabeticView(PaginatorView):
    template_name = "alphabetic_listings.html"

    def get_queryset(self):
        self.concepts = (
            Property.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                concept__namespace__heading='Concepts'
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'concept__code', 'name')
        )
        return super(AlphabeticView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(AlphabeticView, self).get_context_data(**kwargs)
        context.update({"ns_version": Term.objects.get_ns().version})

        return context


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


class GemetSchemaView(XMLTemplateView):
    template_name = 'gemet_schema.rdf'


class GemetVoidView(XMLTemplateView):
    template_name = 'void.rdf'

    def get_context_data(self, **kwargs):
        context = super(GemetVoidView, self).get_context_data(**kwargs)

        context.update({
            'languages': Language.objects.values('code').order_by('code')
        })
        return context


class BackboneRDFView(XMLTemplateView):
    template_name = 'downloads/backbone.rdf'

    def get_context_data(self, **kwargs):
        context = super(BackboneRDFView, self).get_context_data(**kwargs)

        supergroup_uri = Namespace.objects.get(heading='Super groups').type_url
        supergroups = SuperGroup.objects.values('code')

        group_uri = Namespace.objects.get(heading='Groups').type_url
        groups = (Group.objects
                  .filter(source_relations__property_type__name='broader')
                  .values('source_relations__target__code', 'code'))

        theme_uri = Namespace.objects.get(heading='Themes').type_url
        themes = Theme.objects.values('code')

        relations = {}
        concepts = Term.objects.values('id', 'code')

        for concept in concepts:
            relations.update({
                concept['code']: (
                    Relation.objects
                    .filter(source_id=concept['id'],
                            property_type__name__in=['theme', 'group'])
                    .values('target__code',
                            'property_type__name')
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
            property_type__name__in=[
                'broader', 'narrower', 'related',
            ]
        ).values(
            'source__code',
            'target__code',
            'property_type__name',
        )

        self.foreign_relations = (
            ForeignRelation.objects
            .filter(
                concept__in=Term.objects.all(),
                property_type__name__in=[
                    'broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch',
                    'relatedMatch',
                ]
            )
        )

        return context


class GemetRelationsView(GemetRelationsMixin):
    template_name = 'downloads/gemet-relations.html'

    def get_context_data(self, **kwargs):
        context = super(GemetRelationsView, self).get_context_data(**kwargs)
        self.foreign_relations = (
            self.foreign_relations
            .filter(
                show_in_html=True,
            ).order_by(
                'label',
            ).values(
                'concept__code', 'property_type__name', 'uri',
            )
        )
        self.relations = list(self.relations)
        for relation in self.foreign_relations:
            d = {'source__code': relation['concept__code'],
                 'property_type__name': relation['property_type__name'],
                 'target__code': relation['uri']}
            self.relations.append(d)

        context.update({
            'relations': sorted(self.relations,
                                key=lambda x: x['source__code']),
        })

        return context


class Skoscore(GemetRelationsMixin, XMLTemplateView):
    template_name = 'downloads/skoscore.rdf'

    def get_context_data(self, **kwargs):
        context = super(Skoscore, self).get_context_data(**kwargs)

        relations = {}

        self.foreign_relations = (
            self.foreign_relations
            .order_by('label',)
            .values('concept__code', 'property_type__name', 'uri',)
        )
        for r in self.relations:
            source_code = r['source__code']
            name = r['property_type__name']
            target_code = (
                ('' if 'Match' in name else 'concept/') +
                r['target__code']
            )
            relations.setdefault(source_code, []).append(
                {'target__code': target_code, 'property_type__name': name}
            )

        for r in self.foreign_relations:
            source_code = r['concept__code']
            name = r['property_type__name']
            target_code = r['uri']
            relations.setdefault(source_code, []).append(
                {'target__code': target_code, 'property_type__name': name}
            )

        context.update({'concept_relations': relations})

        return context


class DefinitionsByLanguage(HeaderMixin, XMLTemplateView):
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
            if properties:
                definitions[concept['code']] = properties

        context.update({'definitions': definitions})
        return context


class GroupsByLanguage(HeaderMixin, XMLTemplateView):
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


class DownloadView(HeaderMixin, FormView):
    template_name = "downloads/download.html"
    form_class = ExportForm

    def get_initial(self):
        return {'language_names': self.language}

    def get_success_url(self):
        return reverse(self.reverse_name, kwargs={'langcode': self.langcode})

    def form_valid(self, form):
        if self.request.POST['type'] == 'definitions':
            self.reverse_name = 'gemet-definitions.rdf'
        elif self.request.POST['type'] == 'groups':
            self.reverse_name = 'gemet-groups.rdf'
        else:
            raise Http404
        self.langcode = form.cleaned_data['language_names'].code
        return super(DownloadView, self).form_valid(form=form)


def download_gemet_rdf(request):
    try:
        f = open(settings.GEMET_RDFGZ_PATH)
    except (IOError, AttributeError):
        raise Http404

    response = StreamingHttpResponse(f, content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename="gemet.rdf.gz"'
    return response


def redirect_old_urls(request, view_name):
    old_new_views = {
        'index_html': 'themes',
        'rdf': 'download',
        'relations': 'groups',
    }
    view = old_new_views.get(view_name, view_name)

    kwargs = {}
    if view in ['themes', 'groups', 'download', 'gemet-definitions.rdf',
                'gemet-groups.rdf', 'alphabets', 'about', 'definition_sources',
                'changes', 'alphabetic', 'search', 'theme_concepts',
                'webservices']:
        langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
        kwargs.update({'langcode': langcode})

    if view_name == 'theme_concepts':
        theme_code = request.GET.get('th')
        kwargs.update({'theme_code': theme_code})

    url = reverse(view, kwargs=kwargs)
    letter = request.GET.get('letter')
    if letter:
        url = '?'.join((url, urlencode({'letter': letter})))

    return redirect(url, permanent=True)


def old_concept_redirect(request):
    langcode = request.GET.get('langcode', DEFAULT_LANGCODE)
    ns = request.GET.get('ns')
    cp = request.GET.get('cp')
    get_object_or_404(Concept, namespace__id=ns, code=cp)
    return redirect(NS_ID_VIEW_MAPPING.get(ns), langcode=langcode, code=cp)


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
        if is_rdf(request):
            return render_rdf(request, cp)
        return redirect(concept_type, langcode=DEFAULT_LANGCODE, code=cp.code)
    else:
        raise Http404


def render_rdf(request, obj):
    context = {
        'concept': obj,
        'base_url': request.build_absolute_uri('/')[:-1],
        'relations': obj.source_relations.order_by('property_type__uri'),
        'properties': obj.properties.order_by('name')
    }
    return render(request, 'concept.rdf', context,
                  content_type='application/rdf+xml')


def error404(request):
    language = Language.objects.get(pk=DEFAULT_LANGCODE)
    response = render(request, '404.html', {'language': language})
    response.status_code = 404
    return response


def error500(request):
    error_type, error_message, _ = sys.exc_info()
    if error_type == Fault:
        context = {'error_message': error_message.faultString}
        template = '400.html'
        status_code = 400
    else:
        context = {}
        template = '500.html'
        status_code = 500
    return render(request, template, context, status=status_code)
