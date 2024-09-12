import base64
import os
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.users.old.paginations import Pagination
from backend.users.models import Follow
from backend.users.old.serializers import UsersSerializer, UserAvatarSerializer, \
    FollowSerializer
# FollowSerializer
from rest_framework import permissions, status

User = get_user_model()

class CustomUserViewSet(UserViewSet):

    # serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = Pagination
    # queryset = User.objects.all()

    # def get_permissions(self):
    #     if self.action in ['retrieve', 'list']:
    #         return (permissions.IsAuthenticatedOrReadOnly(),)
    #     return super().get_permissions()
    def get_queryset(self):
        # pass
        return User.objects.all()

    @action(
        detail=False,
        methods=['put', 'patch'],
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
                                      name=f'avatar{user.username}.png')
            user.avatar.save(f'avatar{user.username}.png', avatar)
            user.save()
            return Response(
                UserAvatarSerializer(user, context={'request': request}).data
            )
        return Response({"errors": "Аватар не предоставлен"},
                        status=status.HTTP_400_BAD_REQUEST)

    @add_avatar.mapping.delete
    def del_avatar(self, request):
        user = request.user
        if user.avatar:
            os.remove(user.avatar.path)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"errors": "У вас нет аватара"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Получаем профиль пользователя."""
        user = self.request.user
        serializer = UsersSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            # url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписка и отписка на/от автора."""
        user = request.user
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == following:
                return Response({"errors": "Нельзя подписаться на самого себя"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, following=following):
                return Response({"errors": "Вы уже подписаны на этого автора"},
                                status=status.HTTP_400_BAD_REQUEST)
            # serializer = FollowSerializer(following, data=request.data,
            #                               context={'request': request})
            # serializer.is_valid(raise_exception=True)
            follow = Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(serializer.data, status=201)
        subscride = Follow.objects.filter(user=user, following=following)
        if subscride.exists():
            subscride.delete()
            return Response(status=204)
        return Response({"errors": "Ошибка отписки"}, status=400)

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            pagination_class=Pagination,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Получаем подписки пользователя."""
        user = request.user
        followings = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(followings)
        serializer = FollowSerializer(pages, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)



# class FollowViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin, viewsets.GenericViewSet):
#     """Viewset модели Follow."""
#
#     serializer_class = FollowSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('following__username',)
#
#     def get_queryset(self):
#         """Получаем подписки пользователя."""
#         return Follow.objects.filter(user=self.request.user)
#
#     def perform_create(self, serializer):
#         """Подписчика получаем от пользователя."""
#         serializer.save(user=self.request.user)