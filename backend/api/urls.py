from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

from recipes.views import IngredientsViewSet, TagsViewSet, RecipiesViewSet

# from users.views import CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes', RecipiesViewSet, basename='recipies')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
    ]