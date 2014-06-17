from django.conf.urls import patterns, url, include

from gemet.thesaurus.views import (
    redirect_old_urls,
    concept_redirect,
    old_concept_redirect,
    DownloadView,
    AboutView,
    ChangesView,
    ThemesView,
    GroupsView,
    DefinitionSourcesView,
    AlphabetsView,
    SearchView,
    RelationsView,
    TermView,
    ThemeView,
    GroupView,
    SuperGroupView,
    ThemeConceptsView,
    AlphabeticView,
    BackboneView,
    BackboneRDFView,
    DefinitionsView,
    GemetGroupsView,
    GemetRelationsView,
    DefinitionsByLanguage,
    GroupsByLanguage,
    GemetThesaurus,
    Skoscore,
    InspireThemesView,
)
from .api import ApiView


urlpatterns = patterns(
    '',
    url(r'^$', ThemesView.as_view()),
    url(r'^gemet/$', ApiView.as_view(), name='api_root'),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^about/$', AboutView.as_view(), name='about'),
        url(r'^changes/$', ChangesView.as_view(), name='changes'),
        url(r'^themes/$', ThemesView.as_view(), name='themes'),
        url(r'^inspire-themes/$', InspireThemesView.as_view(),
            name='inspire-themes'),
        url(r'^groups/$', GroupsView.as_view(), name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', TermView.as_view(),
            name='concept'),
        url(r'^theme/(?P<concept_id>\d+)/$', ThemeView.as_view(),
            name='theme'),
        url(r'^group/(?P<concept_id>\d+)/$', GroupView.as_view(),
            name='group'),
        url(r'^supergroup/(?P<concept_id>\d+)/$', SuperGroupView.as_view(),
            name='supergroup'),
        url(r'^relations/(?P<group_id>\d+)/$', RelationsView.as_view(),
            name='relations'),
        url(r'^theme/(?P<theme_id>\d+)/concepts/$',
            ThemeConceptsView.as_view(),
            name='theme_concepts'
            ),
        url(r'^alphabetic/$', AlphabeticView.as_view(), name='alphabetic'),
        url(r'^alphabets/$', AlphabetsView.as_view(), name='alphabets'),
        url(r'^search/$', SearchView.as_view(), name='search'),
        url(r'^definition_sources/$', DefinitionSourcesView.as_view(),
            name='definition_sources'),
        ])),
    url(r'^exports/', include([
        url(r'^gemet-backbone\.html/$', BackboneView.as_view(),
            name='gemet-backbone.html'),
        url(r'^gemet-backbone\.rdf/$', BackboneRDFView.as_view(),
            name='gemet-backbone.rdf'),
        url(r'^gemet-definitions.html/$', DefinitionsView.as_view(),
            name='gemet-definitions.html'),
        url(r'^gemet-groups\.html/$', GemetGroupsView.as_view(),
            name='gemet-groups.html'),
        url(r'^gemet-relations\.html/$', GemetRelationsView.as_view(),
            name='gemet-relations.html'),
        url(r'^gemet-skoscore\.rdf/$', Skoscore.as_view(),
            name='gemet-skoscore.rdf'),
        url(r'^gemetThesaurus/$', GemetThesaurus.as_view(),
            name='gemetThesaurus'),
        url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
            url(r'^rdf/$', DownloadView.as_view(), name='download'),
            url(r'^gemet-definitions\.rdf/$', DefinitionsByLanguage.as_view(),
                name='gemet-definitions.rdf'),
            url(r'^gemet-groups\.rdf/$', GroupsByLanguage.as_view(),
                name='gemet-groups.rdf'),
            ])),
        ])),
    url(
        r'^(?P<view_name>'
        'index_html|'
        'groups|'
        'rdf|'
        'gemet-backbone\.html|'
        'gemet-backbone\.rdf|'
        'gemet-definitions\.html|'
        'gemet-groups\.html|'
        'gemet-relations\.html|'
        'gemet-skoscore\.rdf|'
        'gemetThesaurus|'
        'gemet-definitions\.rdf|'
        'gemet-groups\.rdf|'
        'inspire_themes'
        ')/$',
        redirect_old_urls,
        name='redirects'
    ),
    url(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
    url(r'^gemet/concept/$', old_concept_redirect,
        name='old_concept_redirect'),
)
