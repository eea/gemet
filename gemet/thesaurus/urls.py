from django.conf.urls import patterns, url, include

from .views import (
    relations,
    theme_concepts,
    alphabetic,
    alphabets,
    redirect_old_urls,
    concept,
    theme,
    group,
    supergroup,
    concept_redirect,
    old_concept_redirect,
    LanguageView,
    ThemesView,
    GroupsView,
    DefinitionSourcesView,
    SearchView,
)


urlpatterns = patterns(
    '',
    url(r'^$', ThemesView.as_view(template_name="themes.html")),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^about/$', LanguageView.as_view(template_name="about.html"),
            name='about'),
        url(r'^themes/$', ThemesView.as_view(template_name="themes.html"),
            name='themes'),
        url(r'^groups/$', GroupsView.as_view(template_name="groups.html"),
            name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^theme/(?P<concept_id>\d+)/$', theme, name='theme'),
        url(r'^group/(?P<concept_id>\d+)/$', group, name='group'),
        url(r'^supergroup/(?P<concept_id>\d+)/$', supergroup,
            name='supergroup'),
        url(r'^relations/(?P<group_id>\d+)/$', relations, name='relations'),
        url(r'^theme/(?P<theme_id>\d+)/concepts/$', theme_concepts,
            name='theme_concepts'),
        url(r'^alphabetic/$', alphabetic, name='alphabetic'),
        url(r'^alphabets/$', alphabets, name='alphabets'),
        url(r'^search/$', SearchView.as_view(template_name="search.html"),
                                             name='search'),
        url(r'^definition_sources/$',
            DefinitionSourcesView.as_view(
                template_name="definition_sources.html"
            ),
            name='definition_sources')
        ])),
    url(r'^(?P<view_name>index_html|groups)$', redirect_old_urls),
    url(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
    url(r'^gemet/concept/$', old_concept_redirect,
        name='old_concept_redirect'),
)
