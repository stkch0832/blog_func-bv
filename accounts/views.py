from django.shortcuts import render, redirect
from . import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import UserActivateToken


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
        messages.success(request, '認証が完了しました、ようこそサンプルブログへ！')
        return render(request, 'accounts/index.html')
    else:
        messages.warning(request, 'トークンが有効ではありません、再度認証を実施してください')
        return render(request, 'accounts/activation_failure.html', context={
            'token':token,
        })
