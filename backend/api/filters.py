from django_filters.rest_framework import filters, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipies, Tags


# class IngredientsFilter(SearchFilter):
#     """Фильтрация для ингредиентов."""
#
#     search_param = 'name'


class RecipiesFilter(FilterSet):
    """Фильтрация для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )
    is_favorited = filters.NumberFilter(
        method='is_favorited_filter'
    )

    class Meta:
        model = Recipies
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Фильтрация для рецептов в списке покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    def is_favorited_filter(self, queryset, name, value):
        """Фильтрация для рецептов в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset
