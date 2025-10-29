from django.db import migrations, models


def set_default_nicknames(apps, schema_editor):
    CustomUser = apps.get_model("users", "CustomUser")
    for user in CustomUser.objects.filter(nickname__isnull=True):
        user.nickname = f"user_{user.id}"
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_customuser_options_alter_customuser_managers_and_more"),
    ]

    operations = [
        migrations.RunPython(set_default_nicknames),
        migrations.AlterField(
            model_name="customuser",
            name="nickname",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
