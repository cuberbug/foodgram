"""
Хранит сериализаторы, используемые для работы API.
"""
import base64
import binascii
from typing import Any, Union

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from food.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription


User = get_user_model()


# DATA >>


class Base64ImageField(serializers.ImageField):
    """
    Поле для обработки изображений, закодированных в формате Base64.

    Позволяет принимать изображения в формате Base64,
    декодировать их и сохранять как файлы.
    """

    def to_internal_value(self, data: Union[str, ContentFile]) -> Any:
        """
        Преобразует данные из формата Base64 в объект ContentFile.

        Если данные представляют собой строку, начинающуюся с 'data:image',
        она рассматривается как изображение в формате Base64.
        Строка разделяется на формат и содержимое изображения,
        затем содержимое декодируется и сохраняется в объекте ContentFile.

        Args:
            data: Строка данных, представляющая изображение в формате Base64.

        Returns:
            Вызывает родительский метод, передав в него изображение
            в виде объекта ContentFile.
        """
        match data:
            case str() if data.startswith('data:image'):
                try:
                    format, imgstr = data.split(';base64,', maxsplit=1)
                    if not imgstr:
                        raise serializers.ValidationError(
                            'Изображение не может быть пустым.'
                        )
                except ValueError:
                    raise serializers.ValidationError(
                        'Неверный формат изображения: ожидается base64.'
                    )

                ext = format.split('/')[-1]

                try:
                    decoded_img = base64.b64decode(imgstr)
                except binascii.Error:
                    raise serializers.ValidationError(
                        'Некорректные данные base64. Проверьте входные данные.'
                    )

                data = ContentFile(decoded_img, name=f'temp.{ext}')
            case _:
                raise serializers.ValidationError(
                    'Полученные данные не являются строкой с изображением.'
                )

        return super().to_internal_value(data)


# User >>

class ShortUserSerializer(serializers.ModelSerializer):
    """Краткая информация о пользователе."""
    class Meta:
        model = User
        fields = (*User.REQUIRED_FIELDS, User.USERNAME_FIELD, 'id')


class CustomUserSerializer(UserSerializer):
    """Сериализатор кастомного пользователя."""
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *User.REQUIRED_FIELDS,
            User.USERNAME_FIELD,
            'id',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Создание нового пользователя."""
    class Meta:
        model = User
        fields = (*User.REQUIRED_FIELDS, User.USERNAME_FIELD, 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False},
        }

    def to_representation(self, instance):
        serializer = ShortUserSerializer(instance)
        return serializer.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.'
            )
        return data

    def to_representation(self, instance):
        return CustomUserSerializer(
            instance.author,
            context=self.context
        ).data


# Tag >>

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


# Ingredient >>

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


# RecipeIngredient >>

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связанных данных рецепта и ингредиентов."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных для сохранения ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)  # << !!! <<============

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'quantity')


# Recipe >>

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'tags',
            'image',
            'cooking_time',
            'ingredients',
            'text',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.is_favorited.filter(
                user=request.user.id, recipe=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в списке покупок."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.is_favorited.filter(
                user=request.user.id, recipe=obj.id
            ).exists()
        )
