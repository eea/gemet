from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'', include('gemet.thesaurus.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'gemet.thesaurus.views.error404'
handler500 = 'gemet.thesaurus.views.error500'
