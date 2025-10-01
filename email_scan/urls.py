from django.urls import path, include
from email_scan import views

urlpatterns = [
    path("", views.email_scan_view, name="email_scan"),
    path("gmail_inbox/", views.gmail_inbox_api, name="gmail_inbox_api"),
    path("gmail_message/<str:msg_id>/", views.gmail_message_api, name="gmail_message_api"),
]