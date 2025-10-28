from django.urls import path
from .views import PostListAPIView, CreatePaymentIntentAPIView, PostListView, SubscribeView

app_name = 'core'

urlpatterns = [
    # HTML страницы
    path('', PostListView.as_view(), name='post_list'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),

    # API endpoints
    path('api/posts/', PostListAPIView.as_view(), name='post-list-api'),
    path('api/create-payment-intent/', CreatePaymentIntentAPIView.as_view(), name='create-payment'),
]