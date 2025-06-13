from django.urls import path
from .views import health, db_health_check, home, hello_world, htmx_demo

urlpatterns = [
    path('health/', health, name='health'),
    path('health/db/', db_health_check, name='db_health_check'),
    path('home/', home, name='home'),
    path('hello/', hello_world, name='hello_world'),
    path('htmx-demo/', htmx_demo, name='htmx_demo'),
] 