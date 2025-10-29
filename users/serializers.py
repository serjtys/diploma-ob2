from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["phone_number", "password", "nickname"]

    def create(self, validated_data):
        # Создаем пользователя с переданным nickname
        user = CustomUser.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
            nickname=validated_data["nickname"],  # Явно передаем nickname
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if not user:
                raise serializers.ValidationError("Неверный номер телефона или пароль")
            data["user"] = user
        return data
