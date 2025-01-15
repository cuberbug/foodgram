"""
Модуль фильтров для API проекта.

Используется для фильтрации рецептов и ингредиентов по тегам,
добавлению в избранное, списку покупок и имени ингредиента.
"""
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from food.models import Ingredient, Recipe, Tag


User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов по тегам, избранному и списку покупок."""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='В избранном'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='В списке покупок'
    )

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

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов по имени."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
