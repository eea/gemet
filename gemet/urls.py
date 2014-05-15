from django.conf.urls import patterns, include, url, handler404

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'', include('gemet.thesaurus.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'gemet.thesaurus.views.error404'
