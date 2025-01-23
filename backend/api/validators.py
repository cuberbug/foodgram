"""
Содержит валидаторы, используемые в API.
"""
from django.core.validators import RegexValidator

MAX_COOKING_TIME: int = 300  # 5 часов
MIN_COOKING_TIME: int = 1
MIN_VALUE_INGREDIENT: int = 1

USERNAME_EMAIL_VALIDATOR = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Это поле может содержать только буквы, цифры и ./@/+/-/_ символы.'
)
