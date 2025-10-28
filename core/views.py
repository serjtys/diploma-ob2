from .models import Post
from rest_framework import generics
from .serializers import PostSerializer
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from django.shortcuts import render
from django.views.generic import ListView

class CreatePaymentIntentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            intent = stripe.PaymentIntent.create(
                amount=5000,  # 50 рублей в копейках
                currency='rub',
                metadata={'user_id': request.user.id}
            )

            # TODO: Создать запись о платеже
            # Payment.objects.create(
            #     user=request.user,
            #     stripe_payment_intent_id=intent.id,
            #     amount=50.00,
            #     status='pending'
            # )

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
            return Post.objects.all()
        else:
            return Post.objects.filter(is_paid=False)

class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.all().select_related('author')
        else:
            return Post.objects.filter(is_paid=False).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['free_posts_count'] = Post.objects.filter(is_paid=False).count()
        context['paid_posts_count'] = Post.objects.filter(is_paid=True).count()

        if self.request.user.is_authenticated:
            try:
                context['user_has_active_subscription'] = self.request.user.subscription.is_active
            except:
                context['user_has_active_subscription'] = False
        else:
            context['user_has_active_subscription'] = False

        return context

class SubscribeView(APIView):
    def get(self, request):
        return render(request, 'core/subscribe.html', {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        })