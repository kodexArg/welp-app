from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/login/', RedirectView.as_view(url=reverse_lazy('core:login'), query_string=True), name='account_login_redirect'),
    path('', include('core.urls')),
    path('desk/', include('welp_desk.urls')),
    path('payflow/', include('welp_payflow.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]

if settings.IS_LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.errors.handler404'
