from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ===== アカウント ===== #
class SignupForm(forms.ModelForm):

    confirm_password = forms.CharField(
        label='確認用パスワード',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password')
        labels = {
            'email': 'メールアドレス',
            'password': 'パスワード'
        }
        widgets = {
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'password': forms.PasswordInput(
                attrs={'class':'form-control'}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に使用されています')
        return email

    def clean_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError('パスワードが一致しません')
        return password

    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'])
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

# ===== プロフィール ===== #
class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='ユーザー名',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )

    class Meta:
        model = Profile
        fields = ('username', 'introduction', 'birth', 'thumbnail',)
        labels = {
            'introduction': '紹介文',
            'birth': '生年月日',
            'thumbnail': 'サムネイル画像'
        }
        widgets = {
            'introduction': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'rows': 6,
                'cols': 50
                }),
            'birth': forms.NumberInput(attrs={
                'class': 'form-control mb-3',
                'type': 'date'
                }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'form-control mb-3',
                })

        }


class ChangeEmailForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password',)
        labels = {
            'email': 'メールアドレス',
            'password': 'パスワード',
        }
        widgets = {
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'password': forms.PasswordInput(
                attrs={'class':'form-control'}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に使用されています')
        return email

