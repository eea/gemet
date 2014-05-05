from django.conf.urls import patterns, url, include
from .views import (
    themes,
    groups,
    concept,
    relations,
    theme_concepts,
    redirect_old_urls,
    concept_redirect,
    alphabetic,
    alphabets,
)


urlpatterns = patterns(
    '',
    url(r'^$', themes),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^themes/$', themes, name='themes'),
        url(r'^groups/$', groups, name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^relations/(?P<group_id>\d+)/$', relations, name='relations'),
        url(r'^theme/(?P<theme_id>\d+)/$', theme_concepts,
            name='theme_concepts'),
        url(r'^alphabetic/$', alphabetic, name='alphabetic'),
        url(r'^alphabets/$', alphabets, name='alphabets'),
        ])),
    url(r'^(?P<view_name>index_html|groups)$', redirect_old_urls),
    url(r'^concept/(?P<concept_code>\d+)$', concept_redirect,
        name='concept_redirect'),
)
