"""
Описывает отображение пользователя в админке.

Дополнительно:
    - RecipeInline: подключает отображение рецептов,
    автором которых является пользователь.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model

from food.models import Recipe
from users.models import Subscription


PAGINATION_SIZE_USER_ADMIN: int = 10

User = get_user_model()


class RecipeInline(admin.TabularInline):
    """Вставка с отображением авторских рецептов."""
    model = Recipe
    fk_name = 'author'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение модели `User` в админ части сайта."""
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_active',
        'is_superuser',
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    inlines = (RecipeInline,)
    list_per_page = PAGINATION_SIZE_USER_ADMIN


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Отображение модели Subscription в админ части сайта."""
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username')
