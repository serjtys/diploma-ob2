from django.urls import path

from .views import (
    CommentCreateView,
    CommentDeleteView,
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    CommentUpdateView,
    CreatePaymentIntentAPIView,
    FollowingPostsView,
    MyFollowingView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListAPIView,
    PostListView,
    PostSearchView,
    PostUpdateView,
    StripeWebhookView,
    SubscribeView,
    UserSearchView,
)

app_name = "core"

urlpatterns = [
    # HTML страницы
    path("", PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path(
        "post/<int:post_id>/comment/",
        CommentCreateView.as_view(),
        name="create_comment",
    ),
    path("my-following/", MyFollowingView.as_view(), name="my_following"),
    path("search/users/", UserSearchView.as_view(), name="user_search"),
    path("search/posts/", PostSearchView.as_view(), name="post_search"),
    path("following/", FollowingPostsView.as_view(), name="following_posts"),
    # API endpoints
    path("api/posts/", PostListAPIView.as_view(), name="post-list-api"),
    path(
        "api/create-payment-intent/",
        CreatePaymentIntentAPIView.as_view(),
        name="create-payment",
    ),
    # WEBHOOK endpoint
    path("api/webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    # API для комментариев
    path(
        "api/posts/<int:post_id>/comments/",
        CommentListCreateAPIView.as_view(),
        name="post-comments-api",
    ),
    path(
        "api/comments/<int:pk>/",
        CommentRetrieveUpdateDestroyAPIView.as_view(),
        name="comment-detail-api",
    ),
    # Управление комментариями
    path(
        "api/comments/<int:comment_id>/update/",
        CommentUpdateView.as_view(),
        name="update_comment",
    ),
    path(
        "api/comments/<int:comment_id>/delete/",
        CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    # Управление постами
    path("post/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
]
