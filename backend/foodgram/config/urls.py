"""
Базовая конфигурация URL в проекте "Фудграм".

Описывает следующие адреса:
    - страницу для доступа к админке;
    - подключение Djoser;
    - переадресацию запросов к API в одноимённое приложение.
"""
from django.contrib import admin
from django.urls import include, path


djoser_auth = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(djoser_auth)),
    path('api/', include('api.urls')),
]
