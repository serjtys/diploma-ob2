from django.urls import path
from .views import UserRegistrationAPIView, CustomTokenObtainPairView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]