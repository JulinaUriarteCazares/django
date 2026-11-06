from django.contrib.auth import password_validation
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Salida de la API: no tiene el campo password."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefono', 'is_active', 'is_staff',
        ]


class UserWriteSerializer(UserSerializer):
    """Entrada del CRUD de usuarios: la contraseña se recibe, pero nunca se devuelve."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        help_text='Obligatoria al crear. Al editar, solo cambia si se envía.',
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['password']

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if self.instance is None and 'password' not in attrs:
            raise serializers.ValidationError({'password': 'Este campo es requerido.'})
        return attrs

    def create(self, validated_data):
        # create_user guarda la contraseña hasheada.
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        # Evita correos que solo cambian en mayúsculas o minúsculas.
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este correo.')
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        return UserSerializer(instance).data


class TokenPairResponseSerializer(serializers.Serializer):
    """Solo documenta en Swagger la respuesta real del login."""

    refresh = serializers.CharField()
    access = serializers.CharField()
