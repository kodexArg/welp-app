from django.urls import path

from .views.home import index, dashboard_view
from .views.auth import login_view, logout_view
from .views.health import health, db_health_check
from .views.demos import hello_world, htmx_demo
from .views.notifications import notifications_view
from .views.dev import (
    dev_view, dev_udns, dev_sectors, dev_desk_categories, 
    dev_payflow_categories, dev_hierarchy, dev_purchase_workflow
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

    path('notifications/', notifications_view, name='notifications'),
    
    path('dev/', dev_view, name='dev'),
    path('dev/udns/', dev_udns, name='dev_udns'),
    path('dev/sectors/', dev_sectors, name='dev_sectors'),
    path('dev/desk-categories/', dev_desk_categories, name='dev_desk_categories'),
    path('dev/payflow-categories/', dev_payflow_categories, name='dev_payflow_categories'),
    path('dev/hierarchy/', dev_hierarchy, name='dev_hierarchy'),
    path('dev/purchase-workflow/', dev_purchase_workflow, name='dev_purchase_workflow'),]