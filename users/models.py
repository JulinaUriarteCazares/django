from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField('correo electrónico', unique=True)
    telefono = models.CharField(
        'teléfono',
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(r'^\+?\d{10,14}$', 'Escribe de 10 a 14 dígitos, con + opcional.'),
        ],
    )

    USERNAME_FIELD = 'email'
    # createsuperuser falla sin username, porque AbstractUser lo sigue exigiendo.
    REQUIRED_FIELDS = ['username']
