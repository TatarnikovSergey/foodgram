from django.contrib.auth import get_user_model
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
# from .filters import IngredientFilter
from .models import Tags, Ingredients
from .permissions import IsStaffOrReadOnly
from .serializers import TagsSerializer, IngredientsSerializer

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

    def get_queryset(self):
        """Получает ингредиент в соответствии с параметрами запроса."""
        queryset = Ingredients.objects.all()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name.lower())
        return queryset
