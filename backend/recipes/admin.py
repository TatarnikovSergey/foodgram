from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (Favorites, Ingredients, IngredientsRecipies, Recipies,
                     ShoppingCart, Tags)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientsRecipiesInline(admin.TabularInline):
    model = IngredientsRecipies
    extra = 1


@admin.register(Recipies)
class RecipiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'show_ingredient',
                    'favorite_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (IngredientsRecipiesInline,)

    def clean(self):
        if not self.cleaned_data.get('ingredients'):
            raise ValidationError(
                {'ingredients': 'Ингредиенты обязательны для рецепта'})

    @admin.display(description='Ингредиенты')
    def show_ingredient(self, obj):
        return ', '.join(
            str(ingredient.name) for ingredient in obj.ingredients.all())

    @admin.display(description='Добавлений в избранное')
    def favorite_count(self, obj):
        """Считает кол-во добавлений рецепта в избранное."""
        return obj.favorites.all().count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
