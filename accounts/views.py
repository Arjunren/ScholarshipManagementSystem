from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"data": {"user": UserSerializer(user).data, "token": Token.objects.create(user=user).key}}, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        user = authenticate(request, username=request.data.get("username", ""), password=request.data.get("password", ""))
        if user is None or not user.is_active:
            return Response({"error": {"code": "INVALID_CREDENTIALS", "message": "Username or password is incorrect"}}, status=401)
        Token.objects.filter(user=user).delete()
        return Response({"data": {"user": UserSerializer(user).data, "token": Token.objects.create(user=user).key}})


class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()
        return Response(status=204)


class MeView(APIView):
    def get(self, request):
        return Response({"data": UserSerializer(request.user).data})

# Create your views here.
