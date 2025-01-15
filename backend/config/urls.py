"""
Базовая конфигурация URL в проекте "Фудграм".

Производит переадресацию запросов к API и обрабатывает админку.
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import include, path, re_path

from food.models import Recipe, SHORT_CODE_LENGTH


def health_check(request):
    """Отдаёт статус 200, используется для проверки здоровья контейнера."""
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path("health/", health_check, name="health_check"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )


def redirect_short_link(request, short_code):
    """Перенаправляет на детальную страницу рецепта по короткому коду."""
    recipe = get_object_or_404(Recipe, short_code=short_code)
    recipe_url = f'/recipes/{recipe.id}'  # type: ignore
    return HttpResponseRedirect(recipe_url)


urlpatterns += [
    re_path(
        rf'^s/(?P<short_code>[a-zA-Z0-9]{{{SHORT_CODE_LENGTH}}})/$',
        redirect_short_link,
        name='short_link_redirect'
    ),
]
