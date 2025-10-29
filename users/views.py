from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, TemplateView, View
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Comment, Post, UserFollow

from .forms import CustomUserCreationForm
from .serializers import UserLoginSerializer, UserRegistrationSerializer

User = get_user_model()


# API Views (для DRF/JWT)
class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer


class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


# Template Views (для HTML страниц)
class UserRegistrationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("core:post_list")


class UserLoginView(View):
    def get(self, request):
        return render(request, "users/login.html")

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            login(request, user)
            return redirect("core:post_list")  # И здесь!
        else:
            return render(
                request,
                "users/login.html",
                {"error": "Неверный номер телефона или пароль"},
            )


class UserLogoutView(View):
    def get(self, request):
        from django.contrib.auth import logout

        logout(request)
        return redirect("core:post_list")


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        if user_id:
            return get_object_or_404(User, id=user_id)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        context["user_posts"] = Post.objects.filter(author=user).order_by("-created_at")
        context["user_comments"] = Comment.objects.filter(author=user).order_by("-created_at")
        context["posts_count"] = context["user_posts"].count()
        context["comments_count"] = context["user_comments"].count()
        context["is_own_profile"] = user == self.request.user

        # Добавляем информацию о подписке
        if not context["is_own_profile"]:
            context["is_following"] = UserFollow.objects.filter(follower=self.request.user, following=user).exists()

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика для дашборда
        context["recent_posts"] = Post.objects.filter(author=user).order_by("-created_at")[:5]
        context["recent_comments"] = Comment.objects.filter(author=user).order_by("-created_at")[:5]
        context["total_posts"] = Post.objects.filter(author=user).count()
        context["total_comments"] = Comment.objects.filter(author=user).count()

        # Статистика по типам постов
        context["free_posts_count"] = Post.objects.filter(author=user, is_paid=False).count()
        context["paid_posts_count"] = Post.objects.filter(author=user, is_paid=True).count()

        return context
