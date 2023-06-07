from django.contrib.auth.models import AbstractUser
from django.db import models

EMAIL_LENGTH = 254
CHARFIELD_LENGTH = 150


class CustomUser(AbstractUser):
    """Custom-модель пользователя """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    email = models.EmailField(verbose_name='e-mail адрес',
                              max_length=EMAIL_LENGTH, unique=True)
    username = models.CharField(verbose_name='логин пользователя',
                                max_length=CHARFIELD_LENGTH, unique=True)
    first_name = models.CharField(verbose_name='имя пользователя',
                                  max_length=CHARFIELD_LENGTH, blank=True)
    last_name = models.CharField(verbose_name='фамилия пользователя',
                                 max_length=CHARFIELD_LENGTH, blank=True)

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='unique_email_for_user')
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='author',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['user', 'author']
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
