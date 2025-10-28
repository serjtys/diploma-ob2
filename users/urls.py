from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserRegistrationView, UserLoginView, UserLogoutView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]