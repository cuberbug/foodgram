"""
Базовая конфигурация URL для API "Фудграм".
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet
)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

djoser_auth = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(djoser_auth)),
]
