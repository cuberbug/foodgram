from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя автоматически, если его ещё нет'

    def handle(self, *args, **kwargs):
        username = settings.DJANGO_SUPERUSER_USERNAME
        email = settings.DJANGO_SUPERUSER_EMAIL
        password = settings.DJANGO_SUPERUSER_PASSWORD

        try:
            if not User.objects.filter(username=username).exists():
                self.stdout.write(
                    f'Создание суперпользователя "{username}"...'
                )
                User.objects.create_superuser(
                    username=username,  # type: ignore
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Суперпользователь "{username}" создан.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Суперпользователь "{username}" уже существует.'
                    )
                )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f'Ошибка при создании суперпользователя: {str(e)}'
                )
            )
