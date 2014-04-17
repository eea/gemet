from django.conf.urls import patterns, url, include
from .views import themes, groups, concept, relations, redirect_old


urlpatterns = patterns(
    '',
    url(r'^$', themes, {'langcode': 'en'}),
    url(r'^(?P<langcode>[a-zA-Z-]+)/', include([
        url(r'^themes/$', themes, name='themes'),
        url(r'^groups/$', groups, name='groups'),
        url(r'^concept/(?P<concept_id>\d+)/$', concept, name='concept'),
        url(r'^relations/(?P<group_id>\d+)/$', relations, name='relations'),
        ])),
    url(r'^(?P<view_name>themes|groups|concept|relations)/((?P<id>\d+)/)?$',
        redirect_old),
)
