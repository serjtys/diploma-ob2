from .models import Post
from rest_framework import generics
from .serializers import PostSerializer
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post, Subscription
from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class CreatePaymentIntentAPIView(APIView):
    permission_classes = []  # Временно без аутентификации для теста

    def post(self, request):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            print("🔄 [SERVER] Creating Stripe Payment Intent...")

            # Упрощенный Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=5000,
                currency='rub',
            )

            print(f"✅ [SERVER] Payment Intent created: {intent.id}")
            print(f"🔑 [SERVER] Client Secret: {intent.client_secret}")

            return Response({
                'clientSecret': intent.client_secret
            })

        except Exception as e:
            print(f"❌ [SERVER] Stripe error: {str(e)}")
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
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY
        })

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        print("🎯 WEBHOOK RECEIVED!")
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        # Обрабатываем успешный платеж
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_succeeded(payment_intent)

        return HttpResponse(status=200)

    def handle_payment_succeeded(self, payment_intent):
        user_id = payment_intent['metadata'].get('user_id')
        if user_id:
            try:
                subscription, created = Subscription.objects.get_or_create(
                    user_id=user_id,
                    defaults={
                        'is_active': True,
                        'stripe_payment_intent_id': payment_intent['id']
                    }
                )
                if not created:
                    subscription.is_active = True
                    subscription.stripe_payment_intent_id = payment_intent['id']
                    subscription.save()

                print(f"✅ Subscription activated for user {user_id}")
            except Exception as e:
                print(f"❌ Error activating subscription: {e}")