import os
import re
import sys
from itertools import chain
from urllib import urlencode
from xmlrpclib import Fault

from django.http import Http404, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views import View
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.conf import settings

from gemet.thesaurus.models import Concept, DefinitionSource, Group, Language
from gemet.thesaurus.models import InspireTheme, Namespace, Property, SuperGroup
from gemet.thesaurus.models import Term, Theme, Version
from gemet.thesaurus.collation_charts import unicode_character_map
from gemet.thesaurus.forms import SearchForm, ExportForm
from gemet.thesaurus.utils import search_queryset, exp_decrypt, is_rdf
from gemet.thesaurus import DEFAULT_LANGCODE, NR_CONCEPTS_ON_PAGE
from gemet.thesaurus import NS_ID_VIEW_MAPPING
from gemet.thesaurus import PUBLISHED, PENDING, DELETED_PENDING


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


class VersionMixin(object):

    def __init__(self, *args, **kwargs):
        super(VersionMixin, self).__init__(*args, **kwargs)
        self.current_version = Version.objects.get(is_current=True)
        self.pending_version = Version.under_work()

    def get_context_data(self, **kwargs):
        context = super(VersionMixin, self).get_context_data(**kwargs)
        context.update({
            'version': self.current_version,
        })
        return context


class StatusMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if getattr(self, 'edit_view', False):
                status = [PUBLISHED, PENDING, DELETED_PENDING]
            else:
                status = [PUBLISHED, PENDING]
        else:
            status = [PUBLISHED, DELETED_PENDING]
        self.status_values = status
        return super(StatusMixin, self).dispatch(request, *args, **kwargs)


class AboutView(HeaderMixin, TemplateView):
    template_name = "about.html"


class ChangesView(HeaderMixin, TemplateView):
    template_name = "changes.html"


class WebServicesView(HeaderMixin, TemplateView):
    template_name = 'webservices.html'


class ThemesView(HeaderMixin, VersionMixin, StatusMixin, TemplateView):
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
                status__in=self.status_values,
                concept_id__in=self.model_cls.objects
                    .filter(status__in=self.status_values)
                    .values_list('id', flat=True)
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
            'namespace': self.model_cls.NAMESPACE,
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
        languages = (
            Language.objects
            .filter(
                properties__concept__namespace__heading=InspireTheme.NAMESPACE)
            .distinct()
            .values('code', 'name')
            .order_by('name')
        )
        context.update({
            'languages': languages,
        })
        context['version'] = Namespace.objects.get(
            heading=context['namespace']).version
        return context


class GroupsView(HeaderMixin, VersionMixin, StatusMixin, TemplateView):
    template_name = "groups.html"

    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data(**kwargs)

        supergroups = (
            Property.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                status__in=self.status_values,
                concept_id__in=SuperGroup.objects
                .filter(status__in=self.status_values)
                .values_list('id', flat=True)
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'name')
        )

        context.update({
            "supergroups": supergroups,
            "namespace": Group.NAMESPACE,
            "status_values": self.status_values,
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


class SearchView(HeaderMixin, VersionMixin, StatusMixin, FormView):
    template_name = "search.html"
    form_class = SearchForm

    query = ''
    concepts = []

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        context.update({
            "query": self.query,
            "concepts": self.concepts,
            "namespace": Term.NAMESPACE,
            "status_values": self.status_values,
        })
        return context

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        self.concepts = search_queryset(
            self.query,
            self.language,
            status_values=self.status_values,
        )

        return self.render_to_response(self.get_context_data(form=form))


class RelationsView(HeaderMixin, StatusMixin, VersionMixin, TemplateView):
    template_name = "relations.html"

    def get_context_data(self, **kwargs):
        code = self.kwargs.get('group_code')
        group = get_object_or_404(Group, code=code)
        group.status_list = self.status_values
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
            'namespace': Term.NAMESPACE,
        })
        return context


class ConceptView(HeaderMixin, VersionMixin, StatusMixin, DetailView):
    attributes = ['prefLabel', 'definition', 'scopeNote']
    override_languages = True

    def get_object(self):
        code = self.kwargs.get('code')
        concept = get_object_or_404(self.model, code=code)
        concept.status_list = self.status_values
        concept.set_siblings(self.langcode)
        concept.set_parents(self.langcode)
        concept.translations = (
            Property.objects
            .filter(
                name='prefLabel',
                concept=concept,
                status__in=self.status_values,
            )
            .order_by('language__name')
            .values('language__name', 'value')
        )
        concept.set_attributes(self.langcode, self.attributes)
        concept.url = concept.namespace.url + code

        return concept

    def get_context_data(self, **kwargs):
        context = super(ConceptView, self).get_context_data(**kwargs)

        if self.override_languages:
            languages = (
                Language.objects
                .filter(properties__concept=self.object,
                        properties__value__isnull=False)
                .values('code', 'name')
                .order_by('name')
                .distinct()
            )
            context['languages'] = languages

        context.update({
            "namespace": self.model.NAMESPACE,
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
    attributes = ['prefLabel', 'definition', 'scopeNote', 'source', 'altLabel']

    def get_object(self):
        term = super(TermView, self).get_object()
        if not hasattr(term, 'definition'):
            term.set_attributes(DEFAULT_LANGCODE, ['definition'])
            term.default_definition = True
        return term


class InspireThemeView(ConceptView):
    template_name = "inspire_theme.html"
    model = InspireTheme
    concept_type = 'inspire_theme'
    context_object_name = 'inspire_theme'

    def get_context_data(self, **kwargs):
        context = super(InspireThemeView, self).get_context_data(**kwargs)
        context['version'] = Namespace.objects.get(
            heading=context['namespace']).version
        return context


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


class PaginatorView(HeaderMixin, VersionMixin, StatusMixin, ListView):
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
                status__in=self.status_values,
            )
            .extra(
                select={'first_letter': 'SUBSTR(value, 1, 1)'}
            )
        )
        if theme:
            letters = letters.filter(
                concept_id__in=(
                    theme.source_relations
                    .filter(
                        status__in=self.status_values,
                        property_type__name='themeMember',
                    )
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
        self.theme.status_list = self.status_values
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
            'namespace': Term.NAMESPACE,
        })

        return context


class AlphabeticView(PaginatorView):
    template_name = "alphabetic_listings.html"

    def get_queryset(self):
        self.concepts = (
            Property.objects.filter(
                name='prefLabel',
                language__code=self.langcode,
                status__in=self.status_values,
                concept__namespace__heading='Concepts',
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('id', 'concept__code', 'name')
        )
        return super(AlphabeticView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(AlphabeticView, self).get_context_data(**kwargs)
        context.update({"namespace": Term.NAMESPACE})
        return context


class ConceptSourcesView(StatusMixin, View):
    template_name = 'edit/bits/concept_definition_sources.html'

    def get(self, request, langcode, id):
        concept = Concept.objects.get(id=id)
        concept.status_list = self.status_values
        concept.set_attributes(langcode, ['source'])
        definition_sources = []
        if hasattr(concept, 'source'):
            sources = concept.source.split(' / ')
            for source in sources:
                source = source.strip()
                found = DefinitionSource.objects.filter(abbr=source)
                if found.first():
                    definition_sources.append((source, True))
                else:
                    source = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>',
                                    source)
                    definition_sources.append((str(source), False))

        context = {'definition_sources': definition_sources,
                   'language': Language.objects.get(code=langcode)}

        return render(request, self.template_name, context)


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


class DownloadView(HeaderMixin, VersionMixin, FormView):
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


def download_export_file(request, version, filename):
    filepath = os.path.join(settings.EXPORTS_ROOT, version, filename)
    try:
        f = open(filepath)
    except (IOError, AttributeError):
        raise Http404

    extention = filename.split('.')[-1]
    content_types = {
        'rdf': 'application/rdf+xml',
        'html': "text/html; charset=utf-8",
    }
    content_type = content_types[extention]

    response = StreamingHttpResponse(f, content_type=content_type)
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
        'base_url': settings.GEMET_URL,
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
