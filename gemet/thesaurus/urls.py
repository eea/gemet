from django.conf.urls import url, include
from django.conf import settings

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
    InspireThemeView,
    WebServicesView,
    GemetSchemaView,
    GemetVoidView,
    download_gemet_rdf,
)
from gemet.thesaurus.edit_views import AddForeignRelationView, AddPropertyView
from gemet.thesaurus.edit_views import AddParentRelationView, EditPropertyView
from gemet.thesaurus.edit_views import RemoveParentRelationView
from gemet.thesaurus.edit_views import RemoveForeignRelationView
from gemet.thesaurus.edit_views import RemovePropertyView
from gemet.thesaurus.edit_views import TermEditView

from .api import ApiView


urlpatterns = [
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
        'inspire_themes|'
        'alphabets|'
        'about|'
        'definition_sources|'
        'changes|'
        'search|'
        'alphabetic|'
        'theme_concepts|'
        'relations|'
        'webservices'
        ')$',
        redirect_old_urls,
        name='redirects'
    ),
    url(r'^concept$', old_concept_redirect, name='old_concept_redirect'),
    url(r'^2004/06/gemet-schema\.rdf/?$', GemetSchemaView.as_view(),
        name='gemet_schema'),
    url(r'^void\.rdf/?$', GemetVoidView.as_view()),
    url(r'^gemet\.rdf\.gz/?$', download_gemet_rdf),
    url(r'^(?P<method_name>[a-zA-Z]*)$', ApiView.as_view(), name='api_root'),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^about/$', AboutView.as_view(), name='about'),
        url(r'^changes/$', ChangesView.as_view(), name='changes'),
        url(r'^themes/$', ThemesView.as_view(), name='themes'),
        url(r'^inspire-themes/$', InspireThemesView.as_view(),
            name='inspire_themes'),
        url(r'^groups/$', GroupsView.as_view(), name='groups'),
        url(r'^concept/(?P<code>\d+)$', TermView.as_view(),
            name='concept'),
        url(r'^concept/(?P<code>\d+)/edit$', TermEditView.as_view(),
            name='concept_edit'),
        url(r'^inspire-theme/(?P<code>[a-zA-Z]+)$',
            InspireThemeView.as_view(), name='inspire_theme'),
        url(r'^theme/(?P<code>\d+)$', ThemeView.as_view(),
            name='theme'),
        url(r'^group/(?P<code>\d+)$', GroupView.as_view(),
            name='group'),
        url(r'^supergroup/(?P<code>\d+)$', SuperGroupView.as_view(),
            name='supergroup'),
        url(r'^relations/(?P<group_code>\d+)/$', RelationsView.as_view(),
            name='relations'),
        url(r'^theme/(?P<theme_code>\d+)/concepts/$',
            ThemeConceptsView.as_view(),
            name='theme_concepts'
            ),
        url(r'^alphabetic/$', AlphabeticView.as_view(), name='alphabetic'),
        url(r'^alphabets/$', AlphabetsView.as_view(), name='alphabets'),
        url(r'^search/$', SearchView.as_view(), name='search'),
        url(r'^definition-sources/$', DefinitionSourcesView.as_view(),
            name='definition_sources'),
        url(r'^webservices/$', WebServicesView.as_view(), name='webservices'),
        url(r'^remove-property/(?P<concept_id>\d+)/$',
            RemovePropertyView.as_view(), name='remove_property'),
        url(r'^remove-other/(?P<id>\d+)/$',
            RemoveForeignRelationView.as_view(), name='remove_other'),
        url(r'^remove-parent-concept/(?P<concept_id>\d+)/(?P<parent_id>\d+)/'
            r'(?P<type>[a-zA-Z-]+)/$',
            RemoveParentRelationView.as_view(), name='remove_parent'),
        url(r'^add-parent-concept/(?P<concept_id>\d+)/(?P<type>[a-zA-Z-]+)/$',
            AddParentRelationView.as_view(), name='add_parent'),
        url(r'^add-parent-concept/(?P<concept_id>\d+)/(?P<parent_id>\d+)/'
            r'(?P<type>[a-zA-Z-]+)/$',
            AddParentRelationView.as_view(), name='add_parent'),
        url(r'^add-other-concept/(?P<concept_id>\d+)/$',
            AddForeignRelationView.as_view(), name='add_other'),
        url(r'^edit-property/(?P<concept_id>\d+)/(?P<name>[a-zA-Z-]+)/$',
            EditPropertyView.as_view(), name='edit_property'),
        url(r'^add-property/(?P<concept_id>\d+)/(?P<name>[a-zA-Z-]+)/$',
            AddPropertyView.as_view(), name='add_property'),
        ])),
    url(r'^exports/', include([
        url(r'^gemet-backbone\.html$', BackboneView.as_view(),
            name='gemet-backbone.html'),
        url(r'^gemet-backbone\.rdf$', BackboneRDFView.as_view(),
            name='gemet-backbone.rdf'),
        url(r'^gemet-definitions.html$', DefinitionsView.as_view(),
            name='gemet-definitions.html'),
        url(r'^gemet-groups\.html$', GemetGroupsView.as_view(),
            name='gemet-groups.html'),
        url(r'^gemet-relations\.html$', GemetRelationsView.as_view(),
            name='gemet-relations.html'),
        url(r'^gemet-skoscore\.rdf$', Skoscore.as_view(),
            name='gemet-skoscore.rdf'),
        url(r'^gemetThesaurus/$', GemetThesaurus.as_view(),
            name='gemetThesaurus'),
        url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
            url(r'^rdf$', DownloadView.as_view(), name='download'),
            url(r'^gemet-definitions\.rdf$', DefinitionsByLanguage.as_view(),
                name='gemet-definitions.rdf'),
            url(r'^gemet-groups\.rdf$', GroupsByLanguage.as_view(),
                name='gemet-groups.rdf'),
            ])),
        ])),
    url(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
