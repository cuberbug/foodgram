"""
Хранит сериализаторы, используемые для работы API.
"""
import base64
from typing import Any, Union

from django.core.files.base import ContentFile, File
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Поле для обработки изображений, закодированных в формате Base64.

    Позволяет принимать изображения в формате Base64,
    декодировать их и сохранять как файлы.
    """

    def to_internal_value(self, data: Union[str, File]) -> Any:
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
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr), name=f'temp.{ext}'
                )
            case _:
                pass  # Ничего не делаем, если данные не соответствуют шаблону

        return super().to_internal_value(data)
