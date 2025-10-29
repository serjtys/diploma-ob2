from django.contrib import admin

from .models import Comment, Payment, Post, Subscription, UserFollow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author_nickname",
        "is_paid",
        "moderation_status",
        "created_at",
        "is_published",
    ]
    list_filter = ["moderation_status", "is_paid", "is_published", "created_at"]
    search_fields = ["title", "author__nickname", "content"]
    actions = ["approve_posts", "reject_posts", "publish_posts", "unpublish_posts"]

    def author_nickname(self, obj):
        return obj.author.nickname

    author_nickname.short_description = "Автор"

    def approve_posts(self, request, queryset):
        updated = queryset.update(moderation_status="approved", is_published=True)
        self.message_user(request, f"{updated} постов одобрено и опубликовано")

    approve_posts.short_description = "✅ Одобрить и опубликовать"

    def reject_posts(self, request, queryset):
        updated = queryset.update(moderation_status="rejected", is_published=False)
        self.message_user(request, f"{updated} постов отклонено")

    reject_posts.short_description = "❌ Отклонить"

    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} постов опубликовано")

    publish_posts.short_description = "📤 Опубликовать"

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} постов снято с публикации")

    unpublish_posts.short_description = "📥 Снять с публикации"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "author_nickname",
        "post_title",
        "content_short",
        "moderation_status",
        "is_approved",
        "created_at",
    ]
    list_filter = ["moderation_status", "is_approved", "created_at"]
    search_fields = ["author__nickname", "content", "post__title"]
    actions = [
        "approve_comments",
        "disapprove_comments",
        "moderate_approve",
        "moderate_reject",
    ]

    def author_nickname(self, obj):
        return obj.author.nickname

    author_nickname.short_description = "Автор"

    def post_title(self, obj):
        return obj.post.title[:30] + "..." if len(obj.post.title) > 30 else obj.post.title

    post_title.short_description = "Пост"

    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_short.short_description = "Комментарий"

    # ТВОИ СУЩЕСТВУЮЩИЕ МЕТОДЫ
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} комментариев одобрено")

    approve_comments.short_description = "✅ Одобрить комментарии"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} комментариев заблокировано")

    disapprove_comments.short_description = "❌ Заблокировать комментарии"

    # НОВЫЕ МЕТОДЫ ДЛЯ МОДЕРАЦИИ
    def moderate_approve(self, request, queryset):
        updated = queryset.update(moderation_status="approved", is_approved=True)
        self.message_user(request, f"{updated} комментариев прошло модерацию")

    moderate_approve.short_description = "🟢 Одобрить модерацию"

    def moderate_reject(self, request, queryset):
        updated = queryset.update(moderation_status="rejected", is_approved=False)
        self.message_user(request, f"{updated} комментариев отклонено модератором")

    moderate_reject.short_description = "🔴 Отклонить на модерации"


# Регистрируем остальные модели если нужно
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "is_active", "created_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "status", "created_at"]


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "following", "created_at"]
