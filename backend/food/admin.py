"""
Описывает отображение в админке связанных с едой моделей.

Дополнительно настроены счётчики для рецепта, отображающие
количество добавлений в избранное и в список покупок.
"""
from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from food.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class RecipeAuthorInline(admin.TabularInline):
    """Вставка с отображением автора рецепта."""
    model = User
    fk_name = 'author'


class RecipeIngredientInline(admin.TabularInline):
    """Вставка с отображением ингридиента."""
    model = RecipeIngredient
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели `Recipe` в админ части сайта."""
    list_display = (
        'pub_date',
        'name',
        'author',
        'short_code',
        'cooking_time',
        'favorites_count',
        'shopping_cart_count',
    )
    list_filter = ('tags',)
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _favorites_count=Count('is_favorited'),
            _shopping_cart_count=Count('is_in_shopping_cart')
        )

    @admin.display(
        description='Количество добавлений в избранное',
        ordering='_favorites_count',
    )
    def favorites_count(self, obj):
        """Возвращает количество пользователей,
        добавивших рецепт в избранное.
        """
        return obj._favorites_count

    @admin.display(
        description='В корзине у пользователей',
        ordering='_shopping_cart_count',
    )
    def shopping_cart_count(self, obj):
        """Возвращает количество пользователей,
        добавивших рецепт в список покупок.
        """
        return obj._shopping_cart_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели `Ingredient` в админ части сайта."""
    list_display = ('__str__',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение модели `Tag` в админ части сайта."""
    list_display = ('name', 'slug')
    search_fields = ('name',)
