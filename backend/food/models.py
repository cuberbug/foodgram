"""
Описывает модели, связанные с едой и корзиной для покупок.

Список моделей:
    - Recipe: рецепт;
    - Ingredient: ингредиент;
    - Tag: теги;
    - RecipeIngredient: расширенная связь рецепта с ингредиентом.

Таблицы, созданные под капотом Django:
    - favorite: связь рецепта с `User` для реализации избранного;
    - in_shopping_cart: связь рецепта с `User` для реализации добавления
    рецепта в корзину для покупок.
"""
import random
import string
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import IntegrityError, models

from config.db_indexes import get_indexes_for_model

HEX_LENGTH: int = 7
LONG_LENGTH: int = 200
POSITIVE_VALUE_FOR_VALIDATION: int = 1
SHORT_CODE_LENGTH: int = 3

User = get_user_model()


class NamedModel(models.Model):
    """Абстрактная модель с полем для хранения названия."""
    name = models.CharField('название', max_length=LONG_LENGTH)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class Tag(NamedModel):
    """Модель тегов."""
    slug = models.SlugField('слаг', max_length=LONG_LENGTH, unique=True)

    class Meta:
        indexes = get_indexes_for_model('Tag')
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Ingredient(NamedModel):
    """Модель ингредиента."""
    measurement_unit = models.CharField(
        'единица измерения', max_length=LONG_LENGTH,
    )

    class Meta:
        indexes = get_indexes_for_model('Ingredient')
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Recipe(NamedModel):
    """Модель рецепта."""
    pub_date = models.DateTimeField('дата добавления', auto_now_add=True)
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=[MinValueValidator(POSITIVE_VALUE_FOR_VALIDATION)],
    )
    text = models.TextField('описание')
    image = models.ImageField(
        'фотография рецепта',
        upload_to='food/recipes/',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='ингредиенты',
    )
    is_favorited = models.ManyToManyField(
        User,
        db_table='favorite',
        related_name='favorites',
        verbose_name='наличие рецепта в списке избранного',
        blank=True,
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        db_table='in_shopping_cart',
        related_name='recipes_in_shopping_cart',
        verbose_name='наличие рецепта в списке покупок',
        blank=True,
    )
    short_code = models.CharField(
        'короткий код',
        max_length=SHORT_CODE_LENGTH,
        unique=True,
        editable=False,
    )

    class Meta:
        indexes = get_indexes_for_model('Recipe')
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def _generate_short_code(self):
        """Генерирует уникальный короткий код из 3 символов."""
        for _ in range(10):  # Предотвращение возможных коллизий
            code = ''.join(
                random.choices(
                    string.ascii_letters + string.digits, k=SHORT_CODE_LENGTH
                )
            )
            if not Recipe.objects.filter(short_code=code).exists():
                return code
        raise IntegrityError(
            'Не удалось сгенерировать уникальный короткий код.'
        )

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self._generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} (автор: {self.author}).'


class RecipeIngredient(models.Model):
    """Модель для связи рецепта и ингредиента.

    Имеет дополнительное поле `amount`, в котором хранится количество
    ингредиента в условных единицах, необходимое для приготовления рецепта.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'количество ингредиента',
        validators=[MinValueValidator(POSITIVE_VALUE_FOR_VALIDATION)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]
        indexes = get_indexes_for_model('RecipeIngredient')
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
