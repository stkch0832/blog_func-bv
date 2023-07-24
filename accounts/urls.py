from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('activate_user/<uuid:token>/', views.activate_user, name='activate_user'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),

    path('user_profile/<int:pk>', views.profile_detail, name='profile_detail'),
    path('user_profile/<int:pk>/edit', views.profile_edit, name='profile_edit'),
    path('user/<int:pk>/change_email', views.change_email, name='change_email'),
    path('user/<int:pk>/change_password', views.change_password, name='change_password'),

]
