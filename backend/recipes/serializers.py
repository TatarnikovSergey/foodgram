from rest_framework import  serializers

from .models import Ingredients, Recipies, Tags
from users.serializers import Base64ImageField, UsersSerializer



class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagsSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipies
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
