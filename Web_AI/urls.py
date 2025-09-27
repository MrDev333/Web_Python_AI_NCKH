from django.urls import path, include
from Web_AI import views

urlpatterns = [
    path("scanner/", views.scanner, name="scanner"),
]
