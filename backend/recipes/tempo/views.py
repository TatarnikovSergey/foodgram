# from django.contrib.auth import get_user_model
# from django.db.models import Sum
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
import pyshorteners
# from rest_framework import viewsets, permissions, status
# from rest_framework.decorators import action
# from rest_framework.response import Response

# from .filters import IngredientFilter
# from .models import Tags, Ingredients, Recipies, Favorites, ShoppingCart, \
#     IngredientsRecipies
# from backend.recipes.tempo.permissions import IsStaffOrReadOnly
# from backend.recipes.tempo.serializers import TagsSerializer, IngredientsSerializer, \
#     RecipiesSerializer, \
#     FavoritesSerializer, \
#     ShoppingCartSerializer  # , RecipesReadSerializer  # AddRecipesSerializer

# User = get_user_model()


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
    def download_sopping_cart(self, request):
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

