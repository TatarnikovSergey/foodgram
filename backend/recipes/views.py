from django.contrib.auth import get_user_model
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response

# from .filters import IngredientFilter
from .models import Tags, Ingredients, Recipies
from .permissions import IsStaffOrReadOnly
from .serializers import TagsSerializer, IngredientsSerializer, \
    RecipiesSerializer#, RecipesReadSerializer  # AddRecipesSerializer

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