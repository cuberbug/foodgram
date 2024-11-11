"""
Модуль описывает универсальную модель пользователя и функционал подписок.

Основные классы:
    - User: расширенная модель пользователя с дополнительным полем `avatar`.
    - Subscription: представляет подписку одного пользователя на другого.

Применение:
    Используется в приложениях `food` и `api`.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from config.db_indexes import get_indexes_for_model


class User(AbstractUser):
    """Расширенная модель пользователя."""
    avatar = models.ImageField(
        'аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    """Модель пользовательской подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        indexes = get_indexes_for_model('Subscription')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} подписался на {self.author}'
