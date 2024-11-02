"""
Описывает отображение в админке связанных с едой моделей.

Модели:
- `RecipeAdmin`: дополнительно подсчитывает и выводит информацию о том,
    сколько пользователей добавили рецепт в избранное.
- `RecipeAuthorInline`: подключает отображение пользователя,
    который является автором рецепта.
- `IngredientAdmin`: отображение ингредиентов.
- `TagAdmin`: отображение тегов.
"""
from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from food.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeAuthorInline(admin.TabularInline):
    """Вставка с отображением автора рецепта."""
    model = User
    fk_name = 'author'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели `Recipe` в админ части сайта."""
    list_display = (
        'pub_date',
        'name',
        'author',
        'is_favorited_count',
    )
    list_editable = (
        'pub_date',
        'name',
        'author',
    )
    search_fields = (
        'pub_date',
        'name',
        'author__username',
    )
    list_filter = ('author', 'name', 'tags')
    inlines = (
        RecipeAuthorInline,
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        return queryset.annotate(
            is_favorited_count=Count('is_favorited')
        )

    @admin.display(
        description='Количество добавлений в избранное'
    )
    def is_favorited_count(self, obj):
        """Возвращает количество пользователей,
        добавивших рецепт в избранное.
        """
        return obj.is_favorited.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели `Ingredient` в админ части сайта."""
    list_display = ('__str__',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение модели `Tag` в админ части сайта."""
    list_display = (
        'name',
        'slug',
        'color',
    )
    list_editable = (
        'name',
        'slug',
        'color',
    )
    search_fields = ('name',)
    list_filter = ('name',)
