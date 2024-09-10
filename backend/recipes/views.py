from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
import pyshorteners
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

# from .filters import IngredientFilter
from .models import Tags, Ingredients, Recipies, Favorites, ShoppingCart
from .permissions import IsStaffOrReadOnly
from .serializers import TagsSerializer, IngredientsSerializer, \
    RecipiesSerializer, \
    FavoritesSerializer, \
    ShoppingCartSerializer  # , RecipesReadSerializer  # AddRecipesSerializer

User = get_user_model()


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
    queryset = Ingredients.objects.all()

    def get_queryset(self):
        """Получает ингредиент в соответствии с параметрами запроса."""
        queryset = Ingredients.objects.all()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name.lower())
        return queryset


class RecipiesViewSet(viewsets.ModelViewSet):
    # queryset = Recipies.objects.select_related("author").prefetch_related(
    #     "tags", "ingredients")
    queryset = Recipies.objects.all()
    serializer_class = RecipiesSerializer

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
        """Добавление и удаление рецепта в избранное и покупки"""
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
        """Добавление и удаление рецепта в список покупок."""
        return self.add_or_del_recipe(
            serializer_class=ShoppingCartSerializer,
            request=request,
            pk=pk,
            model=ShoppingCart)




    # def get_serializer_class(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return RecipesReadSerializer
    #     return RecipesSerializer

    # def add_recipe(self, request, model, pk=None):
    #     user = request.user
    #     try:
    #         recipe = Recipies.objects.get(
    #             id=pk
    #         )
    #     except Recipies.DoesNotExist:
    #         error_status = 400
    #         return Response(
    #             status=error_status,
    #             data={'errors': 'Указанного рецепта не существует'}
    #         )
        # if model.objects.filter(
        #         recipe=recipe,
        #         user=user
        # ).exists():
        #     model_name = 'список покупок' if model == ShoppingCart \
        #         else 'избранное'
        #     return Response({'errors': f'Рецепт уже добавлен в {model_name}'},
        #                     status=status.HTTP_400_BAD_REQUEST)
        # obj = model.objects.create(
        #     recipe=recipe,
        #     user=user,
        # )
        # if model == ShoppingCart:
        #     return Response(ShoppingCartSerializer(obj).data,
        #                     status=status.HTTP_201_CREATED)
        #
        # return Response(
        #     data={
        #         'id': recipe.id,
        #         'name': recipe.name,
        #         'cooking_time': recipe.cooking_time,
        #         'image': base64.b64encode(recipe.image.read()).decode('utf-8')
        #     },
        #     status=status.HTTP_201_CREATED
        # )