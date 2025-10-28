from django.urls import path
from .views import PostListAPIView, CreatePaymentIntentAPIView

urlpatterns = [
    path('', PostListAPIView.as_view(), name='post-list'),
    path('create-payment-intent/', CreatePaymentIntentAPIView.as_view(), name='create-payment'),
]