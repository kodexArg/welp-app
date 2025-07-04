from django.urls import path
from . import views

app_name = 'welp_payflow'

urlpatterns = [
    path('', views.home, name='index'),
    path('create/', views.CreateTicketView.as_view(), name='create'),
    path('list/', views.list_tickets, name='list'),
    path('api/select-options/<str:field_type>/', views.SelectOptionsView.as_view(), name='select-options'),
] 