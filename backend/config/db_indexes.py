"""
Реализует получение индексации для активной БД.

Возвращает подходящий вариант индексации для принятой в главную функцию модели.
Использует константы из настроек для определения выбранной базы данных.

Комментарий:
    По факту этот модуль несёт в себе избыточный функционал для проекта.

    В начале он казался отличной идеей, реализацией которой можно похвастаться
    на ревью, но в итоге я совершил ошибку и побежал впереди паровоза:
    сначала написал реализацию, а потом начал разбираться с
    PostgreSQL-специфичными индексами (пригодился только BRIN).
    В итоге модуль выглядит несколько чужеродно и неуклюже,
    но я решил его оставить.

    Надеюсь на понимание.
"""
import logging
from enum import Enum
from typing import TypeAlias

from config.settings import DATABASE_NAME, POSTGRESQL, SQLITE
from django.contrib.postgres.indexes import BrinIndex
from django.db import models

logger = logging.getLogger(__name__)


class ValidateModelName(Enum):
    """Хранит имена моделей, для которых есть индексация.

    Названия переменных должны быть в верхнем регистре
    и соответствовать именам хранимых в них моделей,
    которые должны быть записаны как строки в нижнем регистре.

    Пример:
        MODEL = 'model'
    """
    SUBSCRIPTION = 'subscription'
    TAG = 'tag'
    INGREDIENT = 'ingredient'
    RECIPE = 'recipe'
    RECIPEINGREDIENT = 'recipeingredient'


Indexes: TypeAlias = tuple[models.Index | BrinIndex, ...]
INDEXES_FOR_MODELS: dict[ValidateModelName, dict[str, Indexes]] = {

    ValidateModelName.SUBSCRIPTION: {
        POSTGRESQL: (
            models.Index(fields=('user', 'author')),
        ),
        SQLITE: (
            models.Index(fields=('user', 'author')),
        ),
    },

    ValidateModelName.TAG: {
        POSTGRESQL: (
            models.Index(fields=('name',)),
        ),
        SQLITE: (
            models.Index(fields=('name',)),
        ),
    },

    ValidateModelName.INGREDIENT: {
        POSTGRESQL: (
            models.Index(fields=('name',)),
        ),
        SQLITE: (
            models.Index(fields=('name',)),
        ),
    },

    ValidateModelName.RECIPE: {
        POSTGRESQL: (
            BrinIndex(
                name='recipe_pub_date',
                fields=('pub_date',),
                autosummarize=True,
                pages_per_range=8,
            ),
            models.Index(fields=('name',)),
        ),
        SQLITE: (
            models.Index(fields=('pub_date',)),
            models.Index(fields=('name',)),
        ),
    },

    ValidateModelName.RECIPEINGREDIENT: {
        POSTGRESQL: (
            models.Index(fields=('recipe', 'ingredient')),
            models.Index(fields=('ingredient', 'recipe')),
        ),
        SQLITE: (
            models.Index(fields=('recipe', 'ingredient')),
            models.Index(fields=('ingredient', 'recipe')),
        ),
    },

}


def validate_data(model_name: str) -> bool:
    """Валидирует принятое значение модели."""
    if not isinstance(model_name, str):
        logger.error(f'Принятый объект {model_name=} не является строкой.')
        return False

    model_name = model_name.lower()
    if model_name not in [name.value for name in ValidateModelName]:
        logger.error(
            f'Индексация для модели "{model_name}" не поддерживается.'
        )
        return False

    logger.debug(f'Проверка принятого {model_name=} прошла успешно.')
    return True


def get_indexes_for_model(model_name: str) -> Indexes:
    """Возвращает индексы для принятой модели."""
    if not validate_data(model_name):
        raise ValueError('Принятое имя модели не поддерживается.')

    model = getattr(ValidateModelName, model_name.upper())
    indexes = INDEXES_FOR_MODELS[model][DATABASE_NAME]
    logger.debug(f'Индексация для модели {model_name} успешно подготовлена.')

    return indexes
