from django.db.models import Q
# from django_filters.rest_framework import FilterSet
# from rest_framework import filters
#
# from .models import Ingredients
#
#
# class IngredientFilter(FilterSet):
#     name = filters.SearchFilter()
#
#     class Meta:
#         model = Ingredients
#         fields = ('name',)

    # class Meta:
    #     model = Ingredients
    #     fields = ('name',)
    #
    # def filter_queryset(self, request, queryset, view):
    #     if self.name.value():
    #         queryset = queryset.filter(Q(name__startswith=self.name.value()))
    #         return queryset
    #
    #     return queryset