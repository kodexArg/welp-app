from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views.home import index

urlpatterns = [
    path('', index, name='index'),
    path('core/', include('core.urls')),
    path('welp-desk/', include('welp_desk.urls')),
    path('welp-pay/', include('welp_pay.urls')),
    path('admin/', admin.site.urls),
]

if settings.IS_LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
