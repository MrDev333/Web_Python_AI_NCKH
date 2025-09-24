from django.urls import path, include
from Web_AI import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("scanner/", views.scanner, name="scanner"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),
]
