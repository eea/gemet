from django.conf import settings
from django.urls import path, include, re_path

from gemet.thesaurus import auth_views
from gemet.thesaurus import edit_views
from gemet.thesaurus import views
from gemet.thesaurus.api import ApiView


urlpatterns = [
    # Old URLs redirect
    re_path(
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
        'gemetThesaurus\.rdf|'
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
        views.redirect_old_urls,
        name='redirects'
    ),
    re_path(r'^concept$', views.old_concept_redirect, name='old_concept_redirect'),

    # Downloads
    re_path(r'^2004/06/gemet-schema\.rdf/?$', views.GemetSchemaView.as_view(),
        name='gemet_schema'),
    re_path(r'^void\.rdf/?$', views.GemetVoidView.as_view()),
    re_path(r'^gemet\.rdf\.gz/?$', views.download_gemet_rdf),
    re_path(r'^(?P<version>[\d\.]+|latest)/gemet\.rdf\.gz/?$',
        views.download_gemet_rdf, name='full_gemet'),
    re_path(r'^exports/(?P<version>[\d\.]+|latest)/(?P<filename>[a-zA-Z-\.]*)$',
        views.download_export_file, name='export'),
    re_path(r'^exports/(?P<version>[\d\.]+|latest)/(?P<langcode>[a-zA-Z-]+)/'
        '(?P<filename>[a-zA-Z-\.]+)$',
        views.download_translatable_export_file, name='export_lang'),

    # API
    re_path(r'^(?P<method_name>[a-zA-Z]*)$', ApiView.as_view(), name='api_root'),

    # Translatable URLs
    re_path(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        # Static pages
        re_path(r'^about/$', views.AboutView.as_view(), name='about'),
        re_path(r'^changes/$', views.ChangesView.as_view(), name='changes'),
        re_path(r'^webservices/$', views.WebServicesView.as_view(),
            name='webservices'),
        re_path(r'^alphabets/$', views.AlphabetsView.as_view(), name='alphabets'),

        # Exports
        re_path(r'^exports/rdf/(?P<version>[\d\.]+|latest)$',
            views.DownloadView.as_view(), name='download'),

        # Search
        re_path(r'^search/$', views.SearchView.as_view(), name='search'),

        # List pages
        re_path(r'^groups/$', views.GroupsView.as_view(), name='groups'),
        re_path(r'^themes/$', views.ThemesView.as_view(), name='themes'),
        re_path(r'^inspire-themes/$', views.InspireThemesView.as_view(),
            name='inspire_themes'),
        re_path(r'^relations/(?P<group_code>\d+)/$', views.RelationsView.as_view(),
            name='relations'),
        re_path(r'^theme/(?P<theme_code>\d+)/concepts/$',
            views.ThemeConceptsView.as_view(), name='theme_concepts'),
        re_path(r'^alphabetic/$', views.AlphabeticView.as_view(),
            name='alphabetic'),

        # Detail pages
        re_path(r'^concept/(?P<code>\d+)$', views.TermView.as_view(),
            name='concept'),
        re_path(r'^group/(?P<code>\d+)$', views.GroupView.as_view(),
            name='group'),
        re_path(r'^supergroup/(?P<code>\d+)$', views.SuperGroupView.as_view(),
            name='supergroup'),
        re_path(r'^theme/(?P<code>\d+)$', views.ThemeView.as_view(),
            name='theme'),
        re_path(r'^inspire-theme/(?P<code>[a-zA-Z]+)$',
            views.InspireThemeView.as_view(), name='inspire_theme'),

        # Detail snippets
        re_path(r'^concept/(?P<id>\d+)/sources$',
            views.ConceptSourcesView.as_view(), name='concept_sources'),

        # Publish pages
        re_path(r'^version/release/$', edit_views.ReleaseVersionView.as_view(),
            name='release_version'),
        re_path(r'^change/log/$', edit_views.ChangeLogView.as_view(),
            name='change_log'),
        re_path(r'^concept/(?P<id>\d+)/changes/$',
            edit_views.ConceptChangesView.as_view(),
            name='concept_changes'),

        # Edit concept pages
        re_path(r'^concept/add$', edit_views.AddConceptView.as_view(),
            name='concept_add'),
        re_path(r'^concept/(?P<pk>\d+)/delete$',
            edit_views.DeletePendingConceptView.as_view(),
            name='concept_delete'),
        re_path(r'^concept/(?P<code>\w+)/edit$', edit_views.TermEditView.as_view(),
            name='concept_edit'),
        re_path(r'^group/(?P<code>\d+)/edit$', edit_views.GroupEditView.as_view(),
            name='group_edit'),
        re_path(r'^supergroup/(?P<code>\d+)/edit$',
            edit_views.SuperGroupEditView.as_view(),
            name='supergroup_edit'),
        re_path(r'^theme/(?P<code>\d+)/edit$', edit_views.ThemeEditView.as_view(),
            name='theme_edit'),
        re_path(r'^concepts/except/(?P<id>\d+)/relation/(?P<relation>[a-zA-Z]+)$',
            edit_views.UnrelatedConcepts.as_view(), name='concepts_json'),
        re_path(r'^definition-sources/$', views.DefinitionSourcesView.as_view(),
            name='definition_sources'),
        ])),



    re_path(r'^(?P<langcode>[a-zA-Z-]+)/concept/(?P<id>\d+)/edit/', include([
        re_path(r'^property/type/(?P<name>[a-zA-Z-]+)/edit/$',
            edit_views.EditPropertyView.as_view(), name='edit_property'),
        re_path(r'^property/type/(?P<name>[a-zA-Z-]+)/add$',
            edit_views.AddPropertyView.as_view(), name='add_property')
        ])),

    re_path(r'^property/(?P<pk>\d+)/delete/$',
        edit_views.DeletePropertyView.as_view(), name='delete_property'),

    re_path(r'^concept/(?P<id>\d+)/relation/foreign/add/$',
        edit_views.AddForeignRelationView.as_view(), name='add_other'),
    re_path(r'^relation/foreign/(?P<pk>\d+)/delete/$',
        edit_views.DeleteForeignRelationView.as_view(), name='delete_other'),
    re_path(r'^relation/foreign/(?P<pk>\d+)/restore/$',
        edit_views.RestoreForeignRelationView.as_view(), name='restore_other'),

    re_path(r'^source/(?P<source_id>\d+)/target/(?P<target_id>\d+)/'
        'relation/(?P<relation_type>[a-zA-Z-]+)/', include([
            re_path('add/$', edit_views.AddRelationView.as_view(),
                name='add_relation'),
            re_path(r'delete/$', edit_views.DeleteRelationView.as_view(),
                name='delete_relation'),
            re_path(r'restore/$', edit_views.RestoreRelationView.as_view(),
                name='restore_relation'),
        ])),

    re_path(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$',
        views.concept_redirect,
        name='concept_redirect'),
    re_path(
        r'^import/(?P<import_id>\d+)/start/$',
        views.start_import,
        name='start_import'
    ),
    re_path(r'^auth/login/$', auth_views.LoginView.as_view(), name='login'),
    re_path(r'^auth/logout/$', auth_views.LogoutView.as_view(), name='logout'),
]

# if settings.DEBUG:
#     # import debug_toolbar
#     urlpatterns += [
#         re_path(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
