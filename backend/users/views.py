import base64
import os

from django.core.files.base import ContentFile
from django.shortcuts import render
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .paginations import Pagination
from .models import User, Follow
from .serializers import UsersSerializer, UserAvatarSerializer
    # FollowSerializer
from rest_framework import permissions, mixins, viewsets, filters


class CustomUserViewSet(UserViewSet):

    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = Pagination

    def get_queryset(self):
        # pass
        return User.objects.all()


    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],


    )
    def add_avatar(self, request):
        user = request.user
        # avatar_base64 = request.data.get('avatar')
        if request.data.get('avatar'):
            temp_data = request.data.get('avatar').split(",")[1]
            deroder = base64.b64decode(temp_data)
            avatar = ContentFile(deroder,
                                      name=f'avatar{user.id}.png')
            user.avatar.save(f'avatar{user.id}.png', avatar)
            user.save()
            return Response(
                UserAvatarSerializer(user, context={'request': request}).data
            )
        else:
            return Response({"errors": "Аватар не предоставлен"},
                            status=400)

    @add_avatar.mapping.delete
    def del_avatar(self, request):
        user = request.user
        if user.avatar:
            os.remove(user.avatar.path)
            user.avatar = None
            user.save()
            return Response(status=204)
        else:
            return Response({"errors": "У вас нет аватара"}, status=400)

class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin, viewsets.GenericViewSet):
    """Viewset модели Follow."""

    # serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Получаем подписки пользователя."""
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Подписчика получаем от пользователя."""
        serializer.save(user=self.request.user)