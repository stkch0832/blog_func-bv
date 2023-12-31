from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from  uuid import uuid4
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import random
import string
from datetime import date

# === User === #
class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        self.username = self.generate_random_username()
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        verbose_name='ユーザー名',
        max_length=30,
    )

    email = models.EmailField(
        verbose_name='メールアドレス',
        max_length=50,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def generate_random_username(self, length=10):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username


# === アクティベートトークン === #
class UserActivateTokenManager(models.Manager):

    def activate_user_by_token(self, token):
        current_time = timezone.now()
        user_activate_token = self.filter(
            token=token,
            expired_at__gte=current_time
        ).first()

        if user_activate_token:
            user = user_activate_token.user
            user.is_active = True
            user.save()

        return user_activate_token


class UserActivateToken(models.Model):
    token = models.UUIDField(db_index=True)
    expired_at = models.DateTimeField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
        )

    objects = UserActivateTokenManager()

    class Meta:
        db_table = 'user_activate_token'


@receiver(post_save, sender=User)
def user_authentification(sender, instance, created, **kwargs):
    if created and not instance.username:
        instance.username = instance.generate_random_username()
        instance.save()

    current_time = timezone.now()
    user_activate_token = UserActivateToken.objects.create(
        user=instance,
        token=str(uuid4()),
        expired_at=current_time + timedelta(minutes=5),
    )

    # === 認証メール === #

    subject = 'Thanks regist your account'
    body = render_to_string(
        'accounts/mail_text/signup.txt',context={
            'user_activate_token': user_activate_token.token
        })

    from_email = ['admin@test.com']
    to = [instance.email]

    email = EmailMessage(
        subject,
        body,
        from_email,
        to,
    )
    email.send()


# === プロフィール === #
class Profile(models.Model):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    introduction = models.TextField(
        verbose_name="紹介文",
        max_length=255,
    )
    birth = models.DateField(
        verbose_name="生年月日",
        blank=True,
        null=True,
    )
    age = models.IntegerField(
        verbose_name="年齢",
        null=True,
        blank=True
    )

    @property
    def age(self):
        if self.birth:
            today = date.today()
            return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))
        else:
            return

    thumbnail = models.ImageField(
        upload_to='accounts/user_images/',
        verbose_name="サムネイル",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, birth=None)
        instance.profile = profile
        instance.save()
