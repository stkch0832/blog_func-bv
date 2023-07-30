from django.shortcuts import render, redirect, get_object_or_404
from . import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import User, UserActivateToken, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
import json
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
import random
import string


def index(request):
    return render(request, 'accounts/index.html')

# ===== アカウント ===== #

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


# ===== プロフィール ===== #
@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    user = profile.user
    return render(request, 'accounts/profile_detail.html', context={
        'profile': profile,
        'user': user,
    })


@login_required
def profile_edit(request, pk):
    profile_data = get_object_or_404(Profile, user_id=pk)
    if request.method == 'POST':
        profile_form = forms.ProfileForm(
            request.POST or None,
            request.FILES or None,
            instance=profile_data
        )
        if profile_form.is_valid():
            profile_instance = profile_form.save(commit=False)

            user_instance = profile_instance.user
            user_instance.username = profile_form.cleaned_data['username']
            user_instance.save()

            profile_instance.save()

            messages.success(request, 'プロフィールを更新しました')
            return redirect('accounts:profile_detail', pk=pk )
    else:
        profile_form = forms.ProfileForm(initial={
            'username': profile_data.user.username,
            'introduction': profile_data.introduction,
            'birth': profile_data.birth,
            'thumbnail': profile_data.thumbnail,
        })

    return render(request, 'accounts/profile_form.html', context={
        'profile_form': profile_form,
    })


# ===== メールアドレス ===== #
@login_required
def change_email(request, pk):
    user_data = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        change_email_form = forms.ChangeEmailForm(request.POST or None)
        if change_email_form.is_valid():
                email = change_email_form.cleaned_data.get('email')
                password = change_email_form.cleaned_data.get('password')
                user = authenticate(
                    email = user_data.email,
                    password = password
                )
                if user:
                    user_data.email = email
                    user_data.save()
                    messages.success(request, 'メールアドレスの変更が完了しました')
                    return redirect('accounts:change_email', pk=pk)
                else:
                    change_email_form.add_error('password', 'パスワードが間違っています')
    else:
        change_email_form = forms.ChangeEmailForm(initial={
            'email': user_data.email
        })

    return render(request, 'accounts/changeEmail_form.html', context={
        'change_email_form': change_email_form,
    })


# ===== パスワード ===== #
@login_required
def change_password(request, pk):
    user_data = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        change_password_form = forms.ChangePasswordForm(request.POST or None)
        if change_password_form.is_valid():
            try:
                new_password = change_password_form.cleaned_data['new_password']
                validate_password(new_password, user_data)
                current_password = change_password_form.cleaned_data.get('current_password')

                print(current_password)
                user = authenticate(
                    email=user_data.email,
                    password=current_password,
                )
                if user is not None:
                    user.set_password(new_password)
                    user.save()
                    login(request, user)
                    messages.success(request, 'パスワードの変更が完了しました')
                    return redirect('accounts:change_password', pk=pk)
                else:
                    change_password_form.add_error(None, 'パスワードが間違っています')
            except ValidationError as e:
                change_password_form.add_error('new_password', e)
    else:
        change_password_form = forms.ChangePasswordForm()
    return render(request, 'accounts/changePassword_form.html', context={
        'change_password_form': change_password_form,
    })


# ===== アカウント削除 ===== #
@login_required
def withdrawal(request, pk):
    user_data = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        try:
            # is_active = false
            user_data.is_active = False
            
            # メール通知
            subject = 'Notice of completion of withdrawal process'
            body = render_to_string(
                'accounts/mail_text/withdraw.txt',context={
                    'username': user_data.username,
                })

            from_email = ['admin@test.com']
            to = [user_data.email]

            email = EmailMessage(
                subject,
                body,
                from_email,
                to,
            )
            email.send()

            # email = musk
            new_email = generate_unique_email()
            user_data.email = new_email
            user_data.save()

            # ログアウト
            logout(request)
            messages.success(request, 'アカウント削除の手続きを完了致しました')
            return redirect('accounts:index')

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return render(request, 'accounts/withdrawal.html', context={
            'user_data': user_data,
        })


def generate_unique_email():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=35))
    email = f"{random_string}@{''.join(random.choices(string.ascii_letters + string.digits, k=10))}.com"

    while User.objects.filter(email=email).exists():
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=35))
        email = f"{random_string}@{''.join(random.choices(string.ascii_letters + string.digits, k=10))}.com"

    return email
