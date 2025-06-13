from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='root_home'),
    path('core/', include('core.urls')),
    path('admin/', admin.site.urls),
    # Django components URLs
    path("", include("django_components.urls")),
]

if settings.IS_LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
