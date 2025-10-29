from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source="author.nickname", read_only=True, help_text="Никнейм автора")
    author_avatar = serializers.ImageField(source="author.avatar", read_only=True, help_text="Аватар автора")
    replies = serializers.SerializerMethodField(help_text="Ответы на комментарий")
    can_edit = serializers.SerializerMethodField(help_text="Может ли пользователь редактировать комментарий")

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_nickname",
            "author_avatar",
            "parent",
            "content",
            "created_at",
            "updated_at",
            "is_approved",
            "replies",
            "can_edit",
        ]
        read_only_fields = ["author", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_nickname",
            "is_paid",
            "created_at",
            "comments_count",
            "moderation_status",
        ]
        read_only_fields = ["author", "created_at", "moderation_status"]

    def get_comments_count(self, obj):
        """Количество одобренных комментариев к посту"""
        return obj.comments.filter(moderation_status="approved", is_approved=True).count()
