from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
from .serializers import UserRegistrationSerializer, UserLoginSerializer


# API Views (для DRF/JWT)
class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer


class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


# Template Views (для HTML страниц)
class UserRegistrationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('core:post_list')


class UserLoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            login(request, user)
            return redirect('core:post_list')  # И здесь!
        else:
            return render(request, 'users/login.html', {
                'error': 'Неверный номер телефона или пароль'
            })


class UserLogoutView(View):
    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect('core:post_list')