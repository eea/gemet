from django.conf.urls import patterns, url
from .views import themes_list, index, groups_list, concept


urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^themes/$', themes_list, name='themes_list'),
    url(r'^groups/$', groups_list, name='groups_list'),
    url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
)
