from django.urls import path
from . import views

app_name = 'email_scan'

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('api/messages/', views.api_list_messages, name='api_list_messages'),
    path('api/messages/<str:msg_id>/', views.api_fetch_message, name='api_fetch_message'),
]
