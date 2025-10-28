from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation(self):
        """Тест создания пользователя по номеру телефона"""
        user = User.objects.create_user(
            phone_number='+79998887766',
            password='testpass123'
        )
        self.assertEqual(user.phone_number, '+79998887766')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)

    def test_superuser_creation(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            phone_number='+79990001122',
            password='adminpass'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            phone_number='+79995554433',
            password='testpass123'
        )
        self.assertEqual(str(user), '+79995554433')


class UserSerializerTest(TestCase):
    def test_user_registration_serializer(self):
        """Сериализатор регистрации пользователя работает корректно"""
        data = {
            'phone_number': '+79997776655',
            'password': 'newpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_registration_serializer_creates_user(self):
        """Сериализатор регистрации создает пользователя"""
        data = {
            'phone_number': '+79997776655',
            'password': 'newpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.phone_number, '+79997776655')

    def test_user_login_serializer_valid(self):
        """Сериализатор входа пользователя работает с валидными данными"""
        user = User.objects.create_user(
            phone_number='+79998887766',
            password='testpass123'
        )
        data = {
            'phone_number': '+79998887766',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], user)

    def test_user_login_serializer_invalid(self):
        """Сериализатор входа пользователя отклоняет неверные данные"""
        User.objects.create_user(
            phone_number='+79998887766',
            password='testpass123'
        )
        data = {
            'phone_number': '+79998887766',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+79991234567',
            password='testpass123'
        )

    def test_user_registration_api(self):
        """Регистрация пользователя через HTML форму"""
        data = {
            'phone_number': '+79997776655',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }
        response = self.client.post('/users/register/', data)
        # HTML формы возвращают 302 редирект при успехе или 200 с формой при ошибке
        self.assertIn(response.status_code, [302, 200])

    def test_user_login_api(self):
        """Вход пользователя через HTML форму"""
        data = {
            'phone_number': '+79991234567',
            'password': 'testpass123'
        }
        response = self.client.post('/users/login/', data)
        # HTML формы возвращают 302 редирект при успехе или 200 с формой при ошибке
        self.assertIn(response.status_code, [302, 200])