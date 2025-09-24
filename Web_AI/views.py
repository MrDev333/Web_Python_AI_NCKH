import re
import os
import json
import logging
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm


def home(request):
    return render(request, "Web_AI/home.html")

def about(request):
    return render(request, "Web_AI/about.html")

def contact(request):
    return render(request, "Web_AI/contact.html")
def scanner(request):
    return render(request, "Web_AI/scanner.html")


@login_required
def profile(request):
    return render(request, 'Web_AI/profile.html')

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')
