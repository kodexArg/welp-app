from django.urls import path

from .views.home import index, dashboard_view
from .views.auth import login_view, logout_view
from .views.health import health, db_health_check
from .views.demos import hello_world, htmx_demo

from .views.dev import (
    dev_view, 
    dev_categories_view, 
    dev_purchase_workflow_view,
    dev_playground_view,
    dev_test_users_view
)

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('health/', health, name='health'),
    path('health/db/', db_health_check, name='db_health_check'),
    
    path('hello/', hello_world, name='hello_world'),
    path('htmx-demo/', htmx_demo, name='htmx_demo'),
    
    path('dev/', dev_view, name='dev'),
    path('dev/categories/', dev_categories_view, name='dev_categories'),
    path('dev/purchase-workflow/', dev_purchase_workflow_view, name='dev_purchase_workflow'),
    path('dev/playground/', dev_playground_view, name='dev_playground'),
    path('dev/test-users/', dev_test_users_view, name='dev_test_users'),
]