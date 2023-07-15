from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

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
