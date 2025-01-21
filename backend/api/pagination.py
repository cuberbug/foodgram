"""
Настраиваемая пагинация для API.

Значение пагинации динамично и зависит от заданных параметров
в переменных окружения проекта.
"""
from rest_framework.pagination import PageNumberPagination

from config.settings import PAGINATION_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    """Настройка пагинации."""
    page_size = PAGINATION_SIZE
    page_size_query_param = 'limit'
