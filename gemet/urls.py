from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static

from django.contrib import admin

urlpatterns = [
    re_path(r'', include('gemet.thesaurus.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'gemet.thesaurus.views.error404'
handler500 = 'gemet.thesaurus.views.error500'
