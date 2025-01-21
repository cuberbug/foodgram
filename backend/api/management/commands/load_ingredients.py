import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from food.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV-файла в базу данных.'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'data' / 'ingredients.csv'

        if not file_path.exists():
            raise CommandError(f'Файл {file_path} не найден.')

        try:
            with file_path.open(encoding='utf-8') as csvfile:
                reader = csv.reader(
                    csvfile, delimiter=',',
                    quotechar='"',
                    skipinitialspace=True
                )
                for row in reader:
                    if len(row) != 2:
                        self.stderr.write(
                            f'Пропущена строка с некорректными данными: {row}'
                        )
                        continue

                    name, measurement_unit = row
                    name = name.strip()
                    measurement_unit = measurement_unit.strip()

                    if not name or not measurement_unit:
                        self.stderr.write(
                            f'Пропущена строка с пустыми значениями: {row}'
                        )
                        continue

                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    if created:
                        self.stdout.write(f'Добавлен ингредиент: {ingredient}')
        except Exception as e:
            raise CommandError(f'Ошибка при загрузке ингредиентов: {e}')

        self.stdout.write(
            self.style.SUCCESS('Загрузка ингредиентов завершена.')
        )
