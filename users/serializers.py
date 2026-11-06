from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            # La contraseña no se devuelve en la respuesta.
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        # El modelo User de Django no obliga a que el correo sea único.
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este correo.')
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        # create_user guarda la contraseña hasheada.
        return User.objects.create_user(**validated_data)
