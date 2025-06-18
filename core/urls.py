from django.urls import path
from .views import health, db_health_check, home, hello_world, htmx_demo, login_view, logout_view, dashboard_view, index

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('index/', index, name='index'),
    path('health/', health, name='health'),
    path('health/db/', db_health_check, name='db_health_check'),
    path('home/', home, name='home'),
    path('hello/', hello_world, name='hello_world'),
    path('htmx-demo/', htmx_demo, name='htmx_demo'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
] 