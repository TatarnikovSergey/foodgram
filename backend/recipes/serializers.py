import base64


from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from .models import Ingredients, Recipies, Tags, IngredientsRecipies, \
    ShoppingCart, Favorites
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
    # id = serializers.PrimaryKeyRelatedField(
    id = serializers.ReadOnlyField(
        # read_only=True,
        source='ingredient.id'
    )
    # name = serializers.SlugRelatedField(
    name = serializers.ReadOnlyField(source='ingredient.name')
    # measurement_unit = serializers.SlugRelatedField(
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipies
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipiesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagsSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsRecipiesSerializer(
        many=True,
        source='ingredientsrecipies_set',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipies
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')



    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return Favorites.objects.filter(
            user=request.user.id,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user.id,
            recipe=obj,
        ).exists()

    def add_ingredients(self, ingredients, recipe):
        IngredientsRecipies.objects.bulk_create(
            [IngredientsRecipies(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
                for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipies.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def validate_field(self, field):
        data = self.initial_data.get(field)
        if not data:
            raise serializers.ValidationError(
                {f'Для создания рецепта заполните поле {field}!'})
        if field == 'ingredients':
            ingredients_list = []
            for ingredient in data:
                if ingredient['id'] in ingredients_list:
                    raise serializers.ValidationError({
                    f'{field}': 'Ингредиенты не должны повторяться в рецепте!'})
                ingredients_list.append(ingredient['id'])
                if ingredient['amount'] <= 0:
                    raise serializers.ValidationError({
                        f'{field}': 'Количество не может быть < или = ноль!'})
        if field == 'tags':
            tags_list = []
            for tag in data:
                if tag in tags_list:
                    raise serializers.ValidationError({
                        f'{field}': 'Теги не должны повторяться в рецепте!'})
                tags_list.append(tag)
        return data

    def validate(self, data):
        image = self.initial_data.get('image')
        if not image:
            raise serializers.ValidationError(
                {'image': 'У рецепта должна быть картинка'}
            )
        cook_time = data.get('cooking_time')
        if cook_time <= 0:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления не может быть < 1'}
            )
        data['ingredients'] = self.validate_field('ingredients')
        data['tags'] = self.validate_field('tags')
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image) or ""
        tags_data = self.validated_data.get('tags')
        instance.tags.set(tags_data)
        IngredientsRecipies.objects.filter(recipe=instance).all().delete()
        self.add_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


class FavoriteShoppingShowSerializer(serializers.ModelSerializer):
    """Сериализатор избранного и покупок."""

    image = Base64ImageField()

    class Meta:
        model = Recipies
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное."""

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=['user', 'recipe'],
                )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return FavoriteShoppingShowSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в корзину."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return FavoriteShoppingShowSerializer(
            instance.recipe,
            context={'request': request}
        ).data
