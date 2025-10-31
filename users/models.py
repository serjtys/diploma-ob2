from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


# users/models.py
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    nickname = models.CharField(max_length=50, unique=True, blank=False)  # Убрали blank=True
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)

    username = None
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []  # Убрали nickname из обязательных

    def __str__(self):
        return self.nickname if self.nickname else f"user_{self.id}"

    def save(self, *args, **kwargs):
        # Генерируем nickname если его нет
        if not self.nickname or self.nickname.strip() == "":
            # Сначала сохраняем чтобы получить id
            if self.pk is None:
                super().save(*args, **kwargs)

            # Генерируем уникальный nickname
            base_nickname = f"user_{self.id}"
            nickname = base_nickname
            counter = 1

            # Проверяем уникальность
            while CustomUser.objects.filter(nickname=nickname).exclude(pk=self.pk).exists():
                nickname = f"{base_nickname}_{counter}"
                counter += 1

            self.nickname = nickname
            # Сохраняем снова если это было первое сохранение
            if self.pk:
                super().save(update_fields=['nickname'])
            else:
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def get_display_name(self):
        return self.nickname
