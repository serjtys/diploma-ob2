from .models import Post
from rest_framework import generics
from .serializers import PostSerializer
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment


class CreatePaymentIntentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            intent = stripe.PaymentIntent.create(
                amount=5000,
                currency='rub',
                metadata={'user_id': request.user.id}
            )

            # Payment.objects.create(...)

            return Response({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)
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