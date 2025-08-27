# accounts/views.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

class CsrfCookieView(APIView):
    """ست‌کردن CSRF Cookie برای کلاینت (Next.js ابتدا این را صدا می‌زند)."""
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response({"detail": "CSRF cookie set"})

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # برای امنیت، پس از ثبت‌نام کاربر را خودکار لاگین نمی‌کنیم (می‌توانید تغییر دهید)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginThrottle(throttling.ScopedRateThrottle):
    scope = 'login'

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']
        user = authenticate(request, identifier=identifier, password=password)
        
        if user is None:
            return Response({'detail': 'ایمیل یا رمز عبور نادرست است.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({'detail': 'حساب کاربری غیرفعال است.'}, status=status.HTTP_403_FORBIDDEN)
        auth_login(request, user)  # ایجاد سشن و ست‌کردن کوکی sessionid
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        auth_logout(request)
        return Response({'detail': 'خارج شدید.'}, status=status.HTTP_200_OK)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)