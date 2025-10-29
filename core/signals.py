from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Comment, Post
from .utils import clear_safe_cache


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def clear_cache_on_content_change(sender, **kwargs):
    """Очищаем кэш при изменении контента"""
    try:
        clear_safe_cache()
    except Exception:
        # Игнорируем ошибки кэша в тестах
        pass
