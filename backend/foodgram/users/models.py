"""
Описывает универсальную модель пользователя.

Необходима для API приложения "Фудграм". Реализует функционал подписки
пользователя на других пользователей и управление ролями, которые
делят уровень доступа на базовый и административный.
"""
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.db_config import get_indexes_for_model

MAX_LENGTH_USER_ROLE: int = 20


class User(AbstractUser):
    """Модель пользователя для "Фудграм".

    Расширяет базовую модель полями:
    - аватар (изображение);
    - подписка на другий пользователей;
    - роль для управления уровнем доступа.

    Методы:
        is_admin: Проверяет является ли пользователь администратором.
    """
    class UserRole(models.TextChoices):
        """Модель с описанием возможных ролей пользователя."""
        USER = 'user', _('Пользователь')
        ADMIN = 'admin', _('Администратор')

    avatar = models.ImageField(
        'аватар',
        upload_to='users/avatars/%Y/%m/',
        blank=True,
        null=True,
    )

    is_subscribed = models.ManyToManyField(
        'self',
        symmetrical=False,
        db_table='subscription',
        related_name='subscriptions',
        blank=True,
    )
    role = models.CharField(
        max_length=MAX_LENGTH_USER_ROLE,
        default=UserRole.USER,
        choices=UserRole.choices,
    )

    class Meta:
        indexes = get_indexes_for_model('User')

    @property
    @admin.display(boolean=True)
    def is_admin(self) -> bool:
        """Возвращает True, если роль пользователя – администратор."""
        return self.role == self.UserRole.ADMIN

    def __str__(self) -> str:
        return self.username
