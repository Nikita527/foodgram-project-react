from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (AuthToken, IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
