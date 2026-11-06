from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import (
    RegisterUserSerializer,
    TokenPairResponseSerializer,
    UserSerializer,
    UserWriteSerializer,
)


# Sin esto, Swagger mostraría password en las respuestas porque toma el serializer de entrada.
@method_decorator(name='create', decorator=swagger_auto_schema(responses={201: UserSerializer}))
@method_decorator(name='update', decorator=swagger_auto_schema(responses={200: UserSerializer}))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(responses={200: UserSerializer}))
class UserApiViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UserWriteSerializer
        return UserSerializer


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)


@method_decorator(name='post', decorator=swagger_auto_schema(responses={201: UserSerializer}))
class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer


class LoginView(TokenObtainPairView):
    @swagger_auto_schema(responses={200: TokenPairResponseSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
