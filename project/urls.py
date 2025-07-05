from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('desk/', include('welp_desk.urls')),
    path('payflow/', include('welp_payflow.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]

if settings.IS_LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
