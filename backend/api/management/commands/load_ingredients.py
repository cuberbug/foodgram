import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from food.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV-файла в базу данных.'

    def handle(self, *args, **kwargs):
        # Определяем путь до файла, который находится выше текущего проекта
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        file_path = base_dir / 'data' / 'ingredients.csv'

        # Проверяем, существует ли файл
        if not file_path.exists():
            raise CommandError(f'Файл {file_path} не найден.')

        # Загружаем данные из файла
        try:
            with file_path.open(encoding='utf-8') as csvfile:
                # Указываем настройки для чтения файла без заголовков
                reader = csv.reader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
                for row in reader:
                    if len(row) != 2:  # Проверяем, чтобы было ровно 2 столбца
                        self.stderr.write(f'Пропущена строка с некорректными данными: {row}')
                        continue

                    name, measurement_unit = row
                    name = name.strip()  # Убираем лишние пробелы
                    measurement_unit = measurement_unit.strip()

                    # Проверяем наличие данных
                    if not name or not measurement_unit:
                        self.stderr.write(f'Пропущена строка с пустыми значениями: {row}')
                        continue

                    # Добавляем ингредиент в базу данных
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    if created:
                        self.stdout.write(f'Добавлен ингредиент: {ingredient}')
        except Exception as e:
            raise CommandError(f'Ошибка при загрузке ингредиентов: {e}')

        self.stdout.write(self.style.SUCCESS('Загрузка ингредиентов завершена.'))
