"""
Содержит валидаторы, используемые в API.
"""
from django.core.validators import RegexValidator

USERNAME_EMAIL_VALIDATOR = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Это поле может содержать только буквы, цифры и ./@/+/-/_ символы.'
)
