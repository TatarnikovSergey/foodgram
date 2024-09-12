import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
# from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredients, IngredientsRecipies, Recipies, Tags,
                            ShoppingCart, Favorites)

from users.models import Follow#, User
# from users.serializers import UsersSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор кодировки изображений."""
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CreateUserSerializer(UserCreateSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class UsersSerializer(UserSerializer):
# class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()
    # avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)

    def get_is_subscribed(self, obj):

        user = self.context.get('request').user
        # followers = Follow.objects.filter(following=obj)
        # return followers.filter(user=user).exists()
        # if user.is_anonymous:
        #     return False
        return Follow.objects.filter(user=user.id, following=obj.id).exists()




class UserAvatarSerializer(UsersSerializer):
    class Meta:
        model = User
        fields = ('avatar', )


# class FollowSerializer(serializers.ModelSerializer):
#     """Сериализатор подписки на автора."""
#     class Meta:
#         model = Follow



class FollowSerializer(serializers.ModelSerializer):
# # class FollowSerializer(UsersSerializer):
    """Сериализатор данных подписки."""
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    # avatar = serializers.ImageField(read_only=True, source='following.avatar')
    avatar = serializers.SerializerMethodField()
    recipies = serializers.SerializerMethodField()
    recipies_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar', 'recipies',
                  'recipies_count')

    def get_is_subscribed(self, obj):
        # user = self.context.get('request').user
        return Follow.objects.filter(
            user=obj.user, following=obj.following).exists()
        # pass
#

    # def get_recipies(self, obj):
    #     request = self.context.get('request')
    #     limit = request.GET.get('recipes_limit')
    #     queryset = Recipies.objects.filter(author=obj.following)
    #     if limit:
    #         queryset = queryset[:int(limit)]
    #     return FavoriteShoppingShowSerializer(queryset, many=True).data
#         return Follow.objects.filter(
#             user=obj.user, following=obj.following).exists()
# #         return
# #
#
    def get_recipies_count(self, obj):
        # return obj.following.recipe_set.count()
        pass

    def get_avatar(self, obj):
#         if obj.following.avatar:
#             return obj.following.avatar.url
#         return None
        pass


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')

    # def validate_id(self, value):
    #     if not Ingredients.objects.filter(id=value).exists():
    #         raise serializers.ValidationError("Ингредиент не найден")
    #     return value

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
                if not Ingredients.objects.filter(id=ingredient['id']).exists():
                    raise serializers.ValidationError({
                        f'{field}': 'Такого ингредиента не существует!'})
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
                if not Tags.objects.filter(id=tag).exists():
                    raise serializers.ValidationError({
                        f'{field}': 'Такого тега не существует!'})
        return data

    # def validate_ingredients(self, value):
    #     for ingredient_id in value:
    #         if not Ingredients.objects.filter(id=ingredient_id).exists():
    #             raise serializers.ValidationError("Ингредиент не найден")
    #     return value
    def validate(self, data):
        image = self.initial_data.get('image')
        # cooking_time = self.initial_data.get('cooking_time')
        if not image:
            raise serializers.ValidationError(
                {'image': 'У рецепта должна быть картинка'}
            )
        cook_time = data.get('cooking_time')
        if not cook_time or cook_time <= 0:
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