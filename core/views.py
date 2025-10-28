from rest_framework.permissions import IsAuthenticated
from .models import Post
from rest_framework import generics
from .serializers import PostSerializer

class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Авторизованные пользователи видят все посты
            return Post.objects.all()
        else:
            # Неавторизованные видят только бесплатные
            return Post.objects.filter(is_paid=False)