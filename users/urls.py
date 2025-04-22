from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



app_name = 'users_app'

urlpatterns = [
    path('register/', views.signup, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_view, name='profile'),
  
]
