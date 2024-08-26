from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from azbankgateways.urls import az_bank_gateways_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('visits/', include('visits.urls')),
    path('', include('website.urls')),
    path("bankgateways/", az_bank_gateways_urls()),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

