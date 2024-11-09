"""
Хранит сериализаторы, используемые для работы API.
"""
import base64
import binascii
from typing import Any, Union

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from food.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription


User = get_user_model()

MIN_COOKING_TIME: int = 1


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
            instance.author, context=self.context
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

class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта."""
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

    def _check_recipe_exists(self, queryset) -> bool:
        """
        Проверяет, существует ли рецепт в переданном наборе для текущего
        пользователя.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return queryset.filter(user=request.user.id).exists()
        return False

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""
        return self._check_recipe_exists(obj.is_favorited)

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в списке покупок."""
        return self._check_recipe_exists(obj.is_in_shopping_cart)


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        if not bool(ingredients):
            raise ValidationError(
                'Поле ингредиенты обязательно для заполнения'
            )
        unique_ingredients = {ingredient['id'] for ingredient in ingredients}
        if len(ingredients) != len(unique_ingredients):
            raise ValidationError('Ингредиенты не должны повторяться.')
        return ingredients

    def validate_tags(self, tags):
        if not bool(tags):
            raise ValidationError('Поле теги обязательно для заполнения')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться')
        return tags

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        validated_tags = self.validate_tags(tags)
        validated_ingredients = self.validate_ingredients(ingredients)
        data['tags'] = validated_tags
        data['ingredients'] = validated_ingredients
        return data

    def _create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    quantity=ingredient['quantity']
                )
                for ingredient in ingredients
            ]
        )

    def _add_ingredients_and_tags(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self._create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return validated_data

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user  # type: ignore
        recipe = Recipe.objects.create(
            author=author,
            name=validated_data.pop('name'),
            image=validated_data.pop('image'),
            text=validated_data.pop('text'),
            cooking_time=validated_data.pop('cooking_time')
        )
        self._add_ingredients_and_tags(recipe, validated_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        validated_data = self._add_ingredients_and_tags(
            instance, validated_data
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data
