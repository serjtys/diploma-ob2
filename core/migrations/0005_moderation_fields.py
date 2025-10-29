from django.db import migrations, models


def set_initial_moderation_status(apps, schema_editor):
    Post = apps.get_model("core", "Post")
    Comment = apps.get_model("core", "Comment")

    # Все существующие посты и комментарии считаем одобренными
    Post.objects.update(moderation_status="approved", is_published=True)
    Comment.objects.update(moderation_status="approved")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_alter_comment_options_userfollow"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="post",
            name="moderated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="post",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("pending", "На модерации"),
                    ("approved", "Одобрено"),
                    ("rejected", "Отклонено"),
                ],
                default="approved",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("pending", "На модерации"),
                    ("approved", "Одобрено"),
                    ("rejected", "Отклонено"),
                ],
                default="approved",
                max_length=20,
            ),
        ),
        migrations.RunPython(set_initial_moderation_status),
    ]
