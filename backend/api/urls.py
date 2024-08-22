from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

# from users.views import CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
# router.register(r'users/me', CustomUserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
    ]