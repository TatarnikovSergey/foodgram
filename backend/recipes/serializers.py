import base64

from django.core.files.base import ContentFile
from rest_framework import  serializers

from .models import Ingredients, Recipies, Tags
from users.serializers import UsersSerializer


class Base64ImageField(serializers.ImageField):
    """Сериализатор кодировки изображений в рецептах."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

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

    def get_is_favorited(self, obj):
        pass

    def get_is_in_shopping_cart(self, obj):
        pass
