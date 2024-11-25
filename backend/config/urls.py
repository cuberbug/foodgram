"""
Базовая конфигурация URL в проекте "Фудграм".

Производит переадресацию запросов к API и обрабатывает админку.
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path


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
