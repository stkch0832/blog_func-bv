from django.shortcuts import render, redirect
from . import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import UserActivateToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'accounts/index.html')


def signup(request):
    signup_form = forms.SignupForm(request.POST or None)
    if signup_form.is_valid():
        try:
            signup_form.save()
            messages.success(
                request, '認証メールを送信しましたので、ご確認ください')
            return redirect('accounts:index')
        except ValidationError as e:
            signup_form.add_error('password', e)
    return render(request, 'accounts/signup_form.html', context={
        'signup_form': signup_form,
    })


def activate_user(request, token):
    user_activate_token = UserActivateToken.objects.activate_user_by_token(token)

    if user_activate_token:
        messages.success(request, '認証が完了しました、ログインしてください')
        return render(request, 'accounts/index.html')
    else:
        messages.warning(request, 'トークンが有効ではありません、再度認証を実施してください')
        return render(request, 'accounts/index.html')


def user_login(request):
    login_form = forms.LoginForm(request.POST or None)

    if login_form.is_valid():
        email = login_form.cleaned_data.get('email')
        password = login_form.cleaned_data.get('password')
        user = authenticate(
            email=email,
            password=password
        )

        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'ログインが完了しました')
                return redirect('accounts:index')
            else:
                messages.warning(request, 'アカウント認証が完了していません')
        else:
            messages.warning(request, 'メールアドレスまたはパスワードが間違っています')
    return render(request, 'accounts/login_form.html', context={
            'login_form':login_form,
        })


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'ログアウトしました')
    return redirect('accounts:index')
