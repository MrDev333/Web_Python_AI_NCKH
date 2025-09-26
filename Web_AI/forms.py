from django.contrib.auth.forms import UserCreationForm
from django import forms
from allauth.account.forms import LoginForm


class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields

class MyCustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)
        
        # Thêm các lớp CSS vào trường 'login' và 'password'
        self.fields['login'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Tên đăng nhập hoặc Email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Mật khẩu'
        })