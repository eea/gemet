from django.conf.urls import patterns, url, include

from .views import (
    about,
    themes,
    groups,
    relations,
    theme_concepts,
    alphabetic,
    alphabets,
    redirect_old_urls,
    search,
    concept,
    theme,
    group,
    supergroup,
    concept_redirect,
    old_concept_redirect,
    definition_sources,
)


urlpatterns = patterns(
    '',
    url(r'^$', themes),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^about/$', about, name='about'),
        url(r'^themes/$', themes, name='themes'),
        url(r'^groups/$', groups, name='groups'),
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
        url(r'^search/$', search, name='search'),
        url(r'^definition_sources/$',definition_sources,
            name='definition_sources')
        ])),
    url(r'^(?P<view_name>index_html|groups)$', redirect_old_urls),
    url(r'^(?P<concept_type>\w+)/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
    url(r'^gemet/concept/$', old_concept_redirect,
        name='old_concept_redirect'),
)
