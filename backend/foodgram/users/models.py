from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomUser(AbstractUser):
    """Custom-модель пользователя """

    USER = 'user'
    ADMIN = 'admin'

    # ROLE_CHOICE = (
    #     (USER, 'Авторизованный пользователь'),
    #     (ADMIN, 'Администратор'),
    # )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, unique=True)
    last_name = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
