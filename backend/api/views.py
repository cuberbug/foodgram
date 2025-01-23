"""
Хранит представления, используемые для работы API.
"""
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.serializers import (
    CreateRecipeSerializer, CustomUserReadSerializer, IngredientSerializer,
    RecipeSerializer, SubscriptionCreateSerializer, SubscriptionSerializer,
    TagSerializer,
)
from food.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


# User Views >>

class CustomUserViewSet(UserViewSet):
    """Представление для модели пользователя."""
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        """Определение прав доступа в зависимости от действия."""
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'me':
            return CustomUserReadSerializer
        if self.action == 'avatar' and self.request.method == 'PUT':
            return CustomUserReadSerializer
        if self.action == 'subscribe':
            return SubscriptionCreateSerializer
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        if self.request.method == 'POST':
            return UserCreateSerializer
        return CustomUserReadSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        """Обновление аватара пользователя."""
        serializer = self.get_serializer(
            instance=self.get_instance(),
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        self.request.user.avatar.delete()  # type: ignore
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        page = self.paginate_queryset(
            Subscription.objects.filter(user=request.user)
        )
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        author = self.get_object()
        if Subscription.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.create(
            user=request.user, author=author
        )
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Отписка от пользователя."""
        author = self.get_object()
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Tag Views >>

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Убрать пагинацию


# Ingredient Views >>

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ['name']
    filter_backends = [IngredientFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Убрать пагинацию


# Recipe Views >>


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для модели рецепта."""
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Создание рецепта с указанием автора."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = self.get_object()
        if recipe.is_favorited.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Рецепт уже в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.is_favorited.add(request.user)
        return Response(
            {'detail': 'Рецепт добавлен в избранное.'},
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        """Удаление рецепта из избранного."""
        recipe = self.get_object()
        if not recipe.is_favorited.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.is_favorited.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в корзину покупок."""
        recipe = self.get_object()
        if recipe.is_in_shopping_cart.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Рецепт уже в корзине покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.is_in_shopping_cart.add(request.user)
        return Response(
            {'detail': 'Рецепт добавлен в корзину покупок.'},
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """Удаление рецепта из корзины покупок."""
        recipe = self.get_object()
        if not recipe.is_in_shopping_cart.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Рецепта нет в корзине покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.is_in_shopping_cart.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.short_code}')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Генерация и скачивание списка покупок в формате .txt"""
        recipes = request.user.recipes_in_shopping_cart.all()

        ingredients = {}
        for recipe in recipes:
            for item in RecipeIngredient.objects.filter(recipe=recipe):
                name = (
                    f'{item.ingredient.name} '
                    f'({item.ingredient.measurement_unit})'
                )
                ingredients[name] = ingredients.get(name, 0) + item.amount

        shopping_list = '\n'.join(
            [f'- {name} — {amount}' for name, amount in ingredients.items()]
        )

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response
