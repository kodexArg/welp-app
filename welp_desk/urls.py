from django.urls import path
from . import views

app_name = 'welp_desk'

urlpatterns = [
    path('', views.index, name='index'),
    path('ticket/create/', views.CreateTicketView.as_view(), name='ticket-create-dev'),
    path('list/', views.list_dev, name='list-dev'),
] 