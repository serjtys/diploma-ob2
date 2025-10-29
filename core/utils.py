from django.core.cache import cache
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import UserFollow, Post

User = get_user_model()


def get_followers_count(user):
    return UserFollow.objects.filter(following=user).count()


def get_following_count(user):
    return UserFollow.objects.filter(follower=user).count()


def is_following(follower, following):
    return UserFollow.objects.filter(follower=follower, following=following).exists()


# НОВЫЕ ФУНКЦИИ ДЛЯ БЕЗОПАСНОГО КЭША
def get_cached_popular_authors():
    """Кэшируем ТОЛЬКО публичные данные авторов"""

    cache_key = "popular_authors_public"
    authors = cache.get(cache_key)

    if not authors:
        authors = list(
            User.objects.annotate(post_count=Count("post"))
            .filter(
                post_count__gt=0,
                post__moderation_status="approved",
                post__is_published=True,
            )
            .order_by("-post_count")[:5]
        )

        cache.set(cache_key, authors, 60 * 15)

    return authors


def get_cached_posts_statistics():
    """Кэшируем ТОЛЬКО общую статистику"""

    cache_key = "posts_statistics"
    stats = cache.get(cache_key)

    if not stats:
        stats = {
            "total_posts": Post.objects.filter(moderation_status="approved", is_published=True).count(),
            "free_posts": Post.objects.filter(is_paid=False, moderation_status="approved", is_published=True).count(),
            "paid_posts": Post.objects.filter(is_paid=True, moderation_status="approved", is_published=True).count(),
            "total_authors": User.objects.filter(post__moderation_status="approved", post__is_published=True)
            .distinct()
            .count(),
        }
        cache.set(cache_key, stats, 60 * 10)

    return stats


def clear_safe_cache():
    """Очищаем ТОЛЬКО безопасный кэш"""
    cache.delete("popular_authors_public")
    cache.delete("posts_statistics")
