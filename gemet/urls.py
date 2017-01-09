from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'', include('gemet.thesaurus.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

handler404 = 'gemet.thesaurus.views.error404'
handler500 = 'gemet.thesaurus.views.error500'
