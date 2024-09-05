import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import  serializers

from .models import Ingredients, Recipies, Tags, IngredientsRecipies
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


class IngredientsRecipiesSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = IngredientsRecipies
        fields = '__all__'


class AddIngredientsRecipiesSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsRecipies
        fields = ('id', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    # tags = TagsSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = AddIngredientsRecipiesSerializer(many=True)
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

    def create_ingredients(self, ingredients, recipe):
        print(ingredients)
        for ingredient in ingredients:
            IngredientsRecipies.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipies.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    # def create(self, validated_data):
    #     # current_user = self.context["request"].user
    #     tags = validated_data.pop("tags")
    #     ingredients = validated_data.pop("ingredients", [])
    #     recipe = Recipies.objects.create(**validated_data)#, author=current_user)
    #     recipe.tags.set(tags)
    #     self.create_ingredients(recipe, ingredients)
    #     return recipe
    # def create_ingredients(self, ingredients, recipe):
    #     for ingredient in ingredients:
    #         IngredientsRecipies.objects.create(
    #             recipe=recipe,
    #             ingredient=ingredient.get('id'),
    #             amount=ingredient.get('amount'),
    #         )
    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     recipe = Recipies.objects.create(**validated_data)
    #     ingredients = validated_data.pop('ingredients')
    #     recipe.save()
    #     recipe.tags.set(tags)
    #     self.create_ingredients(ingredients, recipe)
    #     return recipe
    # def create_ingredients(self, ingredients, recipe):
    #     for ingredient in ingredients:
    #         IngredientAmount.objects.create(
    #             recipe=recipe,
    #             ingredient_id=ingredient.get('id'),
    #             amount=ingredient.get('amount'),
    #         )
    # def validate(self, data):
    #     data['ingredients'] = self.validate_field('ingredients', Ingredients)
    #     data['tags'] = self.validate_field('tags', Tags)
    #     return data
    # @transaction.atomic
    # def create(self, validated_data):
    #     ingredients_data = validated_data.pop('ingredients')
    #     tags_data = validated_data.pop('tags')
    #     recipe = Recipies.objects.create(**validated_data)
    #     recipe.tags.set(tags_data)
    #     self.create_ingredients(ingredients_data, recipe)
    #     return recipe
# class RecipesSerializer(serializers.ModelSerializer):
#     """Сериализатор рецептов."""
#     author = UsersSerializer(read_only=True)
#     ingredients = AddIngredientsRecipiesSerializer(many=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     image = Base64ImageField()
#
#     class Meta:
#         model = Recipies  # Убедитесь, что это правильное имя модели
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
#                   'is_in_shopping_cart', 'name', 'image', 'text',
#                   'cooking_time')
#
#     def get_is_favorited(self, obj):
#         # Реализуйте логику здесь
#         return False
#
#     def get_is_in_shopping_cart(self, obj):
#         # Реализуйте логику здесь
#         return False
#
#     def create_ingredients(self, ingredients, recipe):
#         for ingredient in ingredients:
#             IngredientsRecipies.objects.create(
#                 recipe=recipe,
#                 ingredient_id=ingredient.get('id'),  # Используйте ingredient_id
#                 amount=ingredient.get('amount'),
#             )
#
#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')
#         recipe = Recipies.objects.create(**validated_data)  # Убедитесь, что это правильное имя модели
#         recipe.tags.set(tags_data)
#         self.create_ingredients(ingredients_data, recipe)
#         return recipe


















# class AddIngredientsRecipiesSerializer(serializers.ModelSerializer):
#     """Сериализатор добавления ингредиентов в рецепт."""
#     id = serializers.PrimaryKeyRelatedField(
#         queryset=Ingredients.objects.all(), source='ingredient_id'
#     )
#     amount = serializers.IntegerField()
#
#     class Meta:
#         model = IngredientsRecipies
#         fields = ('id', 'amount')
#
# class RecipesSerializer(serializers.ModelSerializer):
#     """Сериализатор рецептов."""
#     author = UsersSerializer(read_only=True)
#     ingredients = AddIngredientsRecipiesSerializer(many=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     image = Base64ImageField()
#
#     class Meta:
#         model = Recipies  # Убедитесь, что это правильное имя модели
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
#                   'is_in_shopping_cart', 'name', 'image', 'text',
#                   'cooking_time')
#
#     def get_is_favorited(self, obj):
#         # Реализуйте логику здесь
#         return False
#
#     def get_is_in_shopping_cart(self, obj):
#         # Реализуйте логику здесь
#         return False
#
#     def create_ingredients(self, ingredients, recipe):
#         for ingredient in ingredients:
#             IngredientsRecipies.objects.create(
#                 recipe=recipe,
#                 ingredient_id=ingredient.get('id'),  # Используйте ingredient_id
#                 amount=ingredient.get('amount'),
#             )
#
#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')
#         recipe = Recipies.objects.create(**validated_data)  # Убедитесь, что это правильное имя модели
#         recipe.tags.set(tags_data)
#         self.create_ingredients(ingredients_data, recipe)
#         return recipe
#
