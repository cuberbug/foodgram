"""
Модуль фильтров для API проекта.

Используется для фильтрации рецептов и ингредиентов по тегам,
добавлению в избранное, списку покупок и имени ингредиента.
"""
from django.contrib.auth import get_user_model
from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from food.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(rest_framework.FilterSet):
    """Фильтр для рецептов по тегам, избранному и списку покупок."""
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited',
        label='В избранном'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='В списке покупок'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name: str, value: bool):
        """Фильтрует рецепты, добавленные пользователем в избранное."""
        user = self.request.user  # type: ignore
        if value and user.is_authenticated:
            return queryset.filter(is_favorited=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name: str, value: bool):
        """Фильтрует рецепты, добавленные пользователем в список покупок."""
        user = self.request.user  # type: ignore
        if value and user.is_authenticated:
            return queryset.filter(is_in_shopping_cart=user)
        return queryset


class IngredientFilter(SearchFilter):
    """Фильтр для ингредиентов по имени."""
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
