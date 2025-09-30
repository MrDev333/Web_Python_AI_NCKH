import re
import os
import json
import logging
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404


def url_scan_view(request):
    return render(request, "url_scan/url_scan.html")