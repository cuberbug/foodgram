"""
Базовая конфигурация URL для API "Фудграм".
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter


app_name = 'api'

router_v1 = DefaultRouter()

djoser_auth = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(djoser_auth)),
]
