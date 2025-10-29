from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Post, Subscription, UserFollow

User = get_user_model()


# ===== ИСПРАВЛЕННЫЕ ТЕСТЫ МОДЕЛЕЙ =====
class PostModelTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")

    def test_free_post_creation(self):
        """Тест создания бесплатного поста"""
        post = Post.objects.create(
            title="Бесплатный пост",
            content="Бесплатный контент",
            author=self.user,
            is_paid=False,
        )
        self.assertEqual(str(post), post.title)
        self.assertFalse(post.is_paid)
        self.assertEqual(post.author, self.user)
        self.assertIsNotNone(post.created_at)

    def test_paid_post_creation(self):
        """Тест создания платного поста"""
        post = Post.objects.create(
            title="Платный пост",
            content="Платный контент",
            author=self.user,
            is_paid=True,
        )
        self.assertTrue(post.is_paid)
        self.assertEqual(post.author, self.user)


class SubscriptionModelTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")

    def test_subscription_creation(self):
        """Тест создания подписки"""
        subscription = Subscription.objects.create(
            user=self.user, is_active=True, stripe_payment_intent_id="pi_test123"
        )
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.stripe_payment_intent_id, "pi_test123")

    def test_subscription_str_representation(self):
        """Тест строкового представления подписки"""
        subscription = Subscription.objects.create(user=self.user, is_active=True)
        expected_str = f"Subscription for {self.user.phone_number}"
        self.assertEqual(str(subscription), expected_str)


# ===== ИСПРАВЛЕННЫЕ ТЕСТЫ API =====
class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")
        self.free_post = Post.objects.create(
            title="Бесплатный пост",
            content="Бесплатный контент",
            author=self.user,
            is_paid=False,
            moderation_status="approved",
        )
        self.paid_post = Post.objects.create(
            title="Платный пост",
            content="Платный контент",
            author=self.user,
            is_paid=True,
            moderation_status="approved",
        )

    def test_get_posts_unauthenticated(self):
        """Неавторизованные пользователи видят только бесплатные посты"""
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен вернуть только бесплатный пост
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Бесплатный пост")

    def test_get_posts_authenticated(self):
        """Авторизованные пользователи видят все посты"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен вернуть все посты (2)
        self.assertEqual(len(response.data), 2)


class PaymentIntentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_authenticated(self, mock_stripe):
        """Авторизованные пользователи могут создавать платежи (с моком Stripe)"""
        # Мокаем ответ Stripe
        mock_stripe.return_value = type(
            "obj",
            (object,),
            {"id": "pi_test_123", "client_secret": "pi_test_123_secret_abc"},
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/create-payment-intent/")

        # Должен вернуть успех с client_secret
        self.assertEqual(response.status_code, 200)
        self.assertIn("clientSecret", response.data)

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent_stripe_error(self, mock_stripe):
        """Обработка ошибок Stripe"""
        # Мокаем ошибку Stripe
        mock_stripe.side_effect = Exception("Stripe API error")

        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/create-payment-intent/")

        # Должен вернуть ошибку
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)


# ===== ИСПРАВЛЕННЫЕ ТЕСТЫ ПРЕДСТАВЛЕНИЙ =====
class ViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")
        self.client = Client()

    def test_home_page(self):
        """Главная страница доступна без авторизации"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/post_list.html")

    def test_subscribe_page_authenticated(self):
        """Страница подписки доступна авторизованным пользователям"""
        self.client.force_login(self.user)
        response = self.client.get("/subscribe/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/subscribe.html")


# ===== ИСПРАВЛЕННЫЕ ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ =====
class CommentModelTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")
        self.post = Post.objects.create(
            title="Тестовый пост",
            content="Контент",
            author=self.user,
            moderation_status="approved",
        )

    def test_comment_creation(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(post=self.post, author=self.user, content="Тестовый комментарий")
        self.assertEqual(comment.content, "Тестовый комментарий")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertTrue(comment.is_approved)


class UserFollowModelTest(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(phone_number="+79991111111", password="testpass123", nickname="user1")
        self.user2 = User.objects.create_user(phone_number="+79992222222", password="testpass123", nickname="user2")

    def test_user_follow_creation(self):
        """Тест создания подписки на пользователя"""
        follow = UserFollow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)
        self.assertTrue(UserFollow.objects.filter(follower=self.user1, following=self.user2).exists())


class ModerationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")
        self.post = Post.objects.create(
            title="Пост на модерации",
            content="Контент",
            author=self.user,
            moderation_status="pending",
        )

    def test_pending_post_not_visible(self):
        """Посты на модерации не видны в API"""
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пост на модерации не должен отображаться
        post_titles = [post["title"] for post in response.data]
        self.assertNotIn("Пост на модерации", post_titles)

    def test_approved_post_visible(self):
        """Одобренные посты видны в API"""
        self.post.moderation_status = "approved"
        self.post.save()

        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post_titles = [post["title"] for post in response.data]
        self.assertIn("Пост на модерации", post_titles)


class CacheUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")

    def test_get_cached_posts_statistics(self):
        """Тест кэширования статистики"""
        from .utils import get_cached_posts_statistics

        # Создаем тестовые посты для статистики
        Post.objects.create(
            title="Бесплатный пост",
            content="Контент",
            author=self.user,
            is_paid=False,
            moderation_status="approved",
        )
        Post.objects.create(
            title="Платный пост",
            content="Контент",
            author=self.user,
            is_paid=True,
            moderation_status="approved",
        )

        stats = get_cached_posts_statistics()

        self.assertIn("total_posts", stats)
        self.assertIn("free_posts", stats)
        self.assertIn("paid_posts", stats)
        self.assertIn("total_authors", stats)
        self.assertEqual(stats["total_posts"], 2)
        self.assertEqual(stats["free_posts"], 1)
        self.assertEqual(stats["paid_posts"], 1)


class SecurityTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(phone_number="+79991111111", password="testpass123", nickname="user1")
        self.user2 = User.objects.create_user(phone_number="+79992222222", password="testpass123", nickname="user2")
        self.post = Post.objects.create(
            title="Личный пост",
            content="Секретный контент",
            author=self.user1,
            moderation_status="approved",
        )

    def test_cannot_edit_others_posts(self):
        """Пользователь не может редактировать чужие посты"""
        self.client.force_login(self.user2)

        # Попытка доступа к странице редактирования
        response = self.client.get(f"/posts/{self.post.id}/edit/")

        # Должен получить 404 или 403
        self.assertIn(response.status_code, [403, 404])


class SearchFunctionalityTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79991234567", password="testpass123", nickname="testuser")
        self.post = Post.objects.create(
            title="Уникальный пост для поиска",
            content="Содержание поста",
            author=self.user,
            moderation_status="approved",
        )

    def test_post_search(self):
        """Поиск постов работает корректно"""
        response = self.client.get("/search/posts/?q=Уникальный")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Уникальный пост")

    def test_user_search(self):
        """Поиск пользователей работает корректно"""
        response = self.client.get("/search/users/?q=testuser")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
