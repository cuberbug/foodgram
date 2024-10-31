"""
Модуль фильтров для приложения `food`.

Используется для фильтрации рецептов и ингредиентов по тегам,
добавлению в избранное, списку покупок и имени ингредиента.
"""
from django_filters import rest_framework as filters

from food.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов по тегам, избранному и списку покупок."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_list',
    )

    def filter_is_favorited(self, queryset, name: str, value: bool):
        """Фильтрует рецепты по избранному."""
        user = self.request.user  # type: ignore
        if value and user.is_authenticated:
            return queryset.filter(favorites__user_id=user.id)
        return queryset

    def filter_in_shopping_list(self, queryset, name: str, value: bool):
        """Фильтрует рецепты, находящиеся в списке покупок."""
        user = self.request.user  # type: ignore
        if value and user.is_authenticated:
            return queryset.filter(shopping_recipe__user_id=user.id)
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
