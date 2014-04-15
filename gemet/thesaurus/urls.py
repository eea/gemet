from django.conf.urls import patterns, url
from .views import themes_list, index, groups_list, concept, relations


urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(
        r'^(?P<langcode>[a-zA-Z-]+)/themes/$',
        themes_list,
        name='themes_list',
    ),
    url(
        r'^(?P<langcode>[a-zA-Z-]+)/groups/$',
        groups_list,
        name='groups_list',
    ),
    url(
        r'^(?P<langcode>[a-zA-Z-]+)/concept/(?P<concept_id>\d+)/$',
        concept,
        name='concept',
    ),
    url(
        r'^(?P<langcode>[a-zA-Z-]+)/relations/(?P<group_id>\d+)/$',
        relations,
        name='relations',
    ),
)
