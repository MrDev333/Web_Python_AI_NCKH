from django.urls import path, include
from email_scan import views

urlpatterns = [
    path("", views.email_scan_view, name="email_scan"),
]