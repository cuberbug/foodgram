"""
Базовая конфигурация URL в проекте "Фудграм".

Производит переадресацию запросов к API и обрабатывает админку.
"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
