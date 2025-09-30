from django.urls import path, include
from url_scan import views

urlpatterns = [
    path("", views.url_scan_view, name="url_scan"),
]