from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomUser(AbstractUser):
    """Custom-модель пользователя """

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICE = (
        (USER, 'Авторизованный пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    first_name = models.CharField(max_length=30, unique=True)
    last_name = models.CharField(max_length=30, unique=True)
