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

#login 
def signup(request):
    """
    View xử lý việc đăng ký người dùng mới.
    """
    if request.method == 'POST':
        # Nếu người dùng gửi dữ liệu lên
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Nếu form hợp lệ, lưu người dùng vào database
            user = form.save()
            # Tự động đăng nhập cho người dùng ngay sau khi đăng ký thành công
            login(request, user)
            # Chuyển hướng về trang chủ
            return redirect('home') # Thay 'chat_interface' bằng name của trang chủ của bạn
    else:
        # Nếu là GET request, chỉ hiển thị form trống
        form = UserCreationForm()
        
    # Truyền form ra template
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')
