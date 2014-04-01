from django.conf.urls import patterns, url
from .views import themes_list


urlpatterns = patterns('',
    url(r'^$', themes_list, name='themes_list'),
)
