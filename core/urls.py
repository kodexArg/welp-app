from django.urls import path
from .views import health, db_health_check, hello_world, htmx_demo, login_view, logout_view, dashboard_view, index, dev_view

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('health/', health, name='health'),
    path('health/db/', db_health_check, name='db_health_check'),
    path('hello/', hello_world, name='hello_world'),
    path('htmx-demo/', htmx_demo, name='htmx_demo'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dev/', dev_view, name='dev'),
]