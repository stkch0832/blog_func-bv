from django.contrib import admin
from .models import User, UserActivateToken

admin.site.register(User)
admin.site.register(UserActivateToken)
