"""
Хранит представления, используемые для работы API.
"""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionCreateSerializer,
    TagSerializer,
    CreateRecipeSerializer
)
from api.pagination import CustomPageNumberPagination
from food.models import Ingredient, Recipe, Tag
from users.models import Subscription


User = get_user_model()


# User Views >>

class CustomUserViewSet(UserViewSet):
    """Представление для модели пользователя."""
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        serializer = CustomUserSerializer(
            instance=self.get_instance(),
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        self.request.user.avatar.delete()  # type: ignore
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        author = get_object_or_404(User, pk=pk)
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
        serializer = SubscriptionCreateSerializer(
            subscription, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Отписка от пользователя."""
        author = get_object_or_404(User, pk=pk)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
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
