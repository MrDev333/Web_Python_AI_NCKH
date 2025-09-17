from django.urls import path
from Web_AI import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("scanner/", views.scanner, name="scanner"),
    path("signup/", views.signup, name='signup'),
]
