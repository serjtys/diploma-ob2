from django.urls import path

from .views import DashboardView, UserLoginView, UserLogoutView, UserProfileView, UserRegistrationView

app_name = "users"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    # Профили пользователей
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/", UserProfileView.as_view(), name="user_profile"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
