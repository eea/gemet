from django.conf.urls import patterns, url, include
from .views import themes_list, index, groups_list, concept, relations


urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^themes/$', themes_list, name='themes_list'),
        url(r'^groups/$', groups_list, name='groups_list'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^relations/(?P<group_id>\d+)/$', relations, name='relations'),
        ]))
)
