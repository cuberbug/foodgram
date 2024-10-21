"""
Описывает отображение пользователя в админке.

Дополнительно:
- `RecipeInline`: подключает отображение рецептов,
    автором которых является пользователь.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model

from food.models import Recipe

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
        'role',
        'is_superuser',
        'is_active',
    )
    list_editable = (
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
        'is_active',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    inlines = (
        RecipeInline,
    )
