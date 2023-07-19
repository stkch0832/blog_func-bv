from django.contrib import admin
from .models import User, UserActivateToken, Profile

admin.site.register(User)
admin.site.register(UserActivateToken)
admin.site.register(Profile)
