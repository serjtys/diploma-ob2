import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Post, Subscription, UserFollow
from .serializers import CommentSerializer, PostSerializer
from .utils import get_cached_popular_authors, get_cached_posts_statistics

User = get_user_model()
CustomUser = get_user_model()


class CreatePaymentIntentAPIView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Создание платежного интента для Stripe",
        responses={
            200: openapi.Response(
                description="Платежный интент создан",
                examples={"application/json": {"clientSecret": "pi_3ABC123..._secret_xyz789"}},
            ),
            400: openapi.Response(description="Ошибка создания интента"),
        },
    )
    def post(self, request):
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            print("🔄 [SERVER] Creating Stripe Payment Intent...")

            # Упрощенный Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=5000,
                currency="rub",
            )

            print(f"✅ [SERVER] Payment Intent created: {intent.id}")
            print(f"🔑 [SERVER] Client Secret: {intent.client_secret}")

            return Response({"clientSecret": intent.client_secret})

        except Exception as e:
            print(f"❌ [SERVER] Stripe error: {str(e)}")
            return Response({"error": str(e)}, status=400)


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        # Только одобренные и опубликованные посты
        base_queryset = Post.objects.filter(moderation_status="approved", is_published=True)

        if user.is_authenticated:
            return base_queryset
        else:
            return base_queryset.filter(is_paid=False)

    @swagger_auto_schema(
        operation_description="Получить список постов",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    template_name = "core/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    class PostListView(ListView):
        model = Post
        template_name = "core/post_list.html"
        context_object_name = "posts"
        paginate_by = 10

        def get_queryset(self):
            user = self.request.user
            # Только одобренные и опубликованные посты
            base_queryset = Post.objects.filter(moderation_status="approved", is_published=True).select_related(
                "author"
            )

            if user.is_authenticated:
                return base_queryset
            else:
                return base_queryset.filter(is_paid=False)

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # ИСПОЛЬЗУЕМ БЕЗОПАСНЫЙ КЭШ ДЛЯ СТАТИСТИКИ
            stats = get_cached_posts_statistics()
            context.update(
                {
                    "free_posts_count": stats["free_posts"],
                    "paid_posts_count": stats["paid_posts"],
                    "total_posts": stats["total_posts"],
                }
            )

            # ПОЛЬЗОВАТЕЛЬСКИЕ ДАННЫЕ - БЕЗ КЭША!
            if self.request.user.is_authenticated:
                try:
                    context["user_has_active_subscription"] = self.request.user.subscription.is_active
                except Exception as e:
                    print(f"❌ [SERVER] Stripe error: {str(e)}")
            else:
                context["user_has_active_subscription"] = False

            # БЕЗОПАСНЫЙ КЭШ ДЛЯ ПОПУЛЯРНЫХ АВТОРОВ
            context["popular_authors"] = get_cached_popular_authors()

            return context


class SubscribeView(APIView):
    def get(self, request):
        return render(
            request,
            "core/subscribe.html",
            {"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY},
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        print("🎯 WEBHOOK RECEIVED!")
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except ValueError as e:
            print(f"ValueError in webhook: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(f"Stripe signature error: {e}")
            return HttpResponse(status=400)

        # Обрабатываем успешный платеж
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            self.handle_payment_succeeded(payment_intent)

        return HttpResponse(status=200)

    def handle_payment_succeeded(self, payment_intent):
        user_id = payment_intent["metadata"].get("user_id")
        if user_id:
            try:
                subscription, created = Subscription.objects.get_or_create(
                    user_id=user_id,
                    defaults={
                        "is_active": True,
                        "stripe_payment_intent_id": payment_intent["id"],
                    },
                )
                if not created:
                    subscription.is_active = True
                    subscription.stripe_payment_intent_id = payment_intent["id"]
                    subscription.save()

                print(f"✅ Subscription activated for user {user_id}")
            except Exception as e:
                print(f"❌ Error activating subscription: {e}")


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == "POST":
            # Для POST запросов используем SessionAuthentication
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        # Только одобренные комментарии
        queryset = Comment.objects.filter(
            post_id=self.kwargs["post_id"],
            parent__isnull=True,
            moderation_status="approved",
            is_approved=True,
        ).prefetch_related("replies")
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @swagger_auto_schema(
        operation_description="Получить комментарии к посту",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый комментарий",
        request_body=CommentSerializer,
        responses={201: CommentSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(is_approved=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_update(self, serializer):
        # Разрешаем редактирование только автору
        if serializer.instance.author == self.request.user:
            serializer.save()

    def perform_destroy(self, instance):
        # Разрешаем удаление только автору
        if instance.author == self.request.user:
            instance.delete()


class PostDetailView(DetailView):
    model = Post
    template_name = "core/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Проверяем подписку пользователя
        if self.request.user.is_authenticated:
            try:
                context["user_has_active_subscription"] = self.request.user.subscription.is_active
            except Exception as e:  # вместо bare except
                print(f"❌ Error activating subscription: {e}")
        else:
            context["user_has_active_subscription"] = False

        user_has_access = (
            not post.is_paid  # бесплатный пост
            or context["user_has_active_subscription"]  # есть подписка
            or self.request.user == post.author  # пользователь - автор поста  ← ДОБАВИЛ
            or self.request.user.is_superuser  # суперпользователь
        )

        # Скрываем контент если нет доступа
        if post.is_paid and not user_has_access:
            context["original_content"] = post.content
            post.content = (
                "🔒 Этот контент доступен только с активной подпиской. "
                "Приобретите подписку, чтобы получить доступ ко всем платным материалам."
            )

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "core/post_form.html"
    fields = ["title", "content", "is_paid"]
    success_url = reverse_lazy("core:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")
        parent_id = request.POST.get("parent")

        if content and content.strip():
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content.strip(),
                parent_id=parent_id if parent_id else None,
            )
            messages.success(request, "✅ Комментарий добавлен!")
        else:
            messages.error(request, "❌ Комментарий не может быть пустым")

        return redirect("core:post_detail", pk=post_id)


class CommentUpdateView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # Проверяем что пользователь - автор комментария
        if comment.author != request.user:
            return JsonResponse({"error": "Недостаточно прав"}, status=403)

        new_content = request.POST.get("content")
        if new_content and new_content.strip():
            comment.content = new_content.strip()
            comment.save()
            return JsonResponse({"success": True, "new_content": comment.content})

        return JsonResponse({"error": "Пустой комментарий"}, status=400)


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # Проверяем что пользователь - автор комментария
        if comment.author != request.user:
            return JsonResponse({"error": "Недостаточно прав"}, status=403)

        comment.delete()
        return JsonResponse({"success": True})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "core/post_form.html"
    fields = ["title", "content", "is_paid"]

    def get_queryset(self):
        # Только автор может редактировать свой пост
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy("core:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "core/post_confirm_delete.html"
    success_url = reverse_lazy("core:post_list")

    def get_queryset(self):
        # Только автор может удалить свой пост
        return Post.objects.filter(author=self.request.user)


class MyFollowingView(LoginRequiredMixin, ListView):
    model = UserFollow
    template_name = "core/my_following.html"
    context_object_name = "following_users"

    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user).select_related("following")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["following_count"] = self.get_queryset().count()
        return context


class UserSearchView(ListView):
    model = CustomUser
    template_name = "core/user_search.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query:
            return CustomUser.objects.filter(Q(nickname__icontains=query) | Q(phone_number__icontains=query)).exclude(
                id=self.request.user.id if self.request.user.is_authenticated else None
            )
        return CustomUser.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class PostSearchView(ListView):
    model = Post
    template_name = "core/post_search.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query) | Q(author__nickname__icontains=query)
            )
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class FollowingPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "core/following_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        # Посты авторов, на которых подписан пользователь
        following_ids = UserFollow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)

        return Post.objects.filter(author_id__in=following_ids).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["following_count"] = UserFollow.objects.filter(follower=self.request.user).count()
        return context
