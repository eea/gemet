from django.conf.urls import patterns, url, include

from .views import (
    theme_concepts,
    alphabetic,
    redirect_old_urls,
    concept,
    theme,
    group,
    supergroup,
    concept_redirect,
    old_concept_redirect,
    AboutView,
    ThemesView,
    GroupsView,
    DefinitionSourcesView,
    AlphabetsView,
    SearchView,
    RelationsView,
)


urlpatterns = patterns(
    '',
    url(r'^$', ThemesView.as_view()),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^about/$', AboutView.as_view(), name='about'),
        url(r'^themes/$', ThemesView.as_view(), name='themes'),
        url(r'^groups/$', GroupsView.as_view(), name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^theme/(?P<concept_id>\d+)/$', theme, name='theme'),
        url(r'^group/(?P<concept_id>\d+)/$', group, name='group'),
        url(r'^supergroup/(?P<concept_id>\d+)/$', supergroup,
            name='supergroup'),
        url(r'^relations/(?P<group_id>\d+)/$', RelationsView.as_view(),
            name='relations'),
        url(r'^theme/(?P<theme_id>\d+)/concepts/$', theme_concepts,
            name='theme_concepts'),
        url(r'^alphabetic/$', alphabetic, name='alphabetic'),
        url(r'^alphabets/$', AlphabetsView.as_view(), name='alphabets'),
        url(r'^search/$', SearchView.as_view(), name='search'),
        url(r'^definition_sources/$', DefinitionSourcesView.as_view(),
            name='definition_sources')
        ])),
    url(r'^(?P<view_name>index_html|groups)$', redirect_old_urls),
    url(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
    url(r'^gemet/concept/$', old_concept_redirect,
        name='old_concept_redirect'),
)
