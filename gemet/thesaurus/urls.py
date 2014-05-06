from django.conf.urls import patterns, url, include
from .views import (
    themes,
    groups,
    relations,
    theme_concepts,
    alphabetic,
    alphabets,
    redirect_old_urls,
    concept, concept_redirect,
    theme, theme_redirect,
    group, group_redirect,
    superGroup, superGroup_redirect
)


urlpatterns = patterns('',
    url(r'^$', themes),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^themes/$', themes, name='themes'),
        url(r'^groups/$', groups, name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^theme/(?P<theme_id>\d+)/$', theme, name='theme'),
        url(r'^group/(?P<group_id>\d+)/$', group, name='group'),
        url(r'^supergroup/(?P<superGroup_id>\d+)/$', superGroup,
            name='superGroup'),
        url(r'^relations/(?P<group_id>\d+)/$', relations, name='relations'),
        url(r'^theme/(?P<theme_id>\d+)/concepts/$', theme_concepts,
            name='theme_concepts'),
        url(r'^alphabetic/$', alphabetic, name='alphabetic'),
        url(r'^alphabets/$', alphabets, name='alphabets'),
        ])),
    url(r'^(?P<view_name>index_html|groups)$', redirect_old_urls),
    url(r'^concept/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
    url(r'^theme/(?P<theme_code>\d+)$', theme_redirect,
        name='theme_redirect'),
    url(r'^group/(?P<group_code>\d+)$', group_redirect,
        name='group_redirect'),
    url(r'^supergroup/(?P<superGroup_code>\d+)$', superGroup_redirect,
        name='superGroup_redirect'),
)
