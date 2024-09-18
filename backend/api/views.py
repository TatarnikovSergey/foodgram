import base64
import os

from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
import pyshorteners

from .filters import RecipiesFilter
from .paginations import Pagination
from .permissions import IsStaffOrReadOnly, IsAuthorOrModerPermission
from .serializers import (FavoritesSerializer, FollowSerializer,
                          IngredientsSerializer, RecipiesSerializer,
                          ShoppingCartSerializer, TagsSerializer,
                          UserAvatarSerializer, UsersSerializer,
                          CreateUserSerializer)
from recipes.models import (Favorites, Ingredients, IngredientsRecipies,
                            Recipies, ShoppingCart, Tags)
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """ViewSet для работы с пользователями."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersSerializer
        elif self.action == 'update':
            return UsersSerializer(partial=True)
        elif self.action == 'create':
            return CreateUserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return User.objects.all()

    @action(
        detail=False,
        methods=['put', 'patch'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_avatar(self, request):
        """Добавляет аватар пользователя."""
        user = request.user
        if request.data.get('avatar'):
            temp_data = request.data.get('avatar').split(",")[1]
            deroder = base64.b64decode(temp_data)
            avatar = ContentFile(deroder, name=f'avatar{user.username}.png')
            user.avatar.save(f'avatar{user.username}.png', avatar)
            user.save()
            return Response(
                UserAvatarSerializer(user, context={'request': request}).data
            )
        return Response({"errors": "Аватар не предоставлен"},
                        status=status.HTTP_400_BAD_REQUEST)

    @add_avatar.mapping.delete
    def del_avatar(self, request):
        """Удаляет аватар пользователя."""
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
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписка и отписка на/от автора."""
        user = request.user
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == following:
                return Response({"errors": "Нельзя подписаться на себя"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, following=following):
                return Response({"errors": "Вы уже подписаны на этого автора"},
                                status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscride = Follow.objects.filter(user=user, following=following)
        if subscride.exists():
            subscride.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"errors": "Ошибка отписки"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            pagination_class=Pagination,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Получаем подписки пользователя."""
        user = request.user
        followings = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(followings)
        serializer = FollowSerializer(pages, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ModelViewSet):
    """ViewSet модели тегов."""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsStaffOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    """ViewSet модели ингредиентов."""
    serializer_class = IngredientsSerializer
    permission_classes = (IsStaffOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        """Получает ингредиент в соответствии с параметрами запроса."""
        queryset = Ingredients.objects.all()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name.lower())
        return queryset


class RecipiesViewSet(viewsets.ModelViewSet):
    """ViewSet модели рецептов."""
    queryset = Recipies.objects.all()
    serializer_class = RecipiesSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipiesFilter
    permission_classes = (IsAuthorOrModerPermission,
                          permissions.IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        """При создании рецепта автора получаем от пользователя."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, pk):
        """Генерация короткой ссылки."""
        get_object_or_404(Recipies, id=pk)
        long_url = request.build_absolute_uri(self.get_extra_action_url_map())
        short = pyshorteners.Shortener()
        short_url = short.tinyurl.short(long_url)
        return Response({'short-link': short_url})

    def add_or_del_recipe(self, serializer_class, request, pk, model):
        """Добавление и удаление рецепта"""
        user = request.user
        recipe = get_object_or_404(Recipies, pk=pk)
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = serializer_class(data=data,
                                      context={'request': request})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт не найден в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Добавление и удаление рецепта в избранное."""
        return self.add_or_del_recipe(
            serializer_class=FavoritesSerializer,
            request=request,
            pk=pk,
            model=Favorites)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецепта в корзину."""
        return self.add_or_del_recipe(
            serializer_class=ShoppingCartSerializer,
            request=request,
            pk=pk,
            model=ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачивание рецептов из корзины."""
        user = request.user
        ingredients = IngredientsRecipies.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        if not ingredients:
            return HttpResponse("Корзина пуста.")
        content = "ИНГРЕДИЕНТЫ:\n"
        for i in ingredients:
            content += (f"{i['ingredient__name']} "
                        f"({i['ingredient__measurement_unit']}) - "
                        f"{i['total_amount']}\n")
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ingredients_list.txt"')
        return response
