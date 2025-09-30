"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from accounts import views as allauth_views
from pages import views as pages_views
from core import views as core_views
from email_scan import views as email_scan_views
from url_scan import views as url_scan_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('pages.urls')),
    path('users/', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path("app/url_scan/", include("url_scan.urls")),
    path("app/email_scan/", include("email_scan.urls")),

]
urlpatterns += staticfiles_urlpatterns()
