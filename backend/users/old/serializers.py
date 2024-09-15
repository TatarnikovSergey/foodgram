# import base64
# from django.core.files.base import ContentFile
# from djoser.serializers import UserCreateSerializer, UserSerializer
#
# # from drf_extra_fields.fields import Base64ImageField
# from rest_framework import serializers
# # from .views import CustomUserViewSet
#
# from .models import User, Follow
# # from recipes.models import Recipies
#
# # from recipes.serializers import FavoriteShoppingShowSerializer
#
#
# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         # Если полученный объект строка, и эта строка
#         # начинается с 'data:image'...
#         if isinstance(data, str) and data.startswith('data:image'):
#             # ...начинаем декодировать изображение из base64.
#             # Сначала нужно разделить строку на части.
#             format, imgstr = data.split(';base64,')
#             # И извлечь расширение файла.
#             ext = format.split('/')[-1]
#             # Затем декодировать сами данные и поместить результат в файл,
#             # которому дать название по шаблону.
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#
#         return super().to_internal_value(data)
#
#
# class CreateUserSerializer(UserCreateSerializer):
#     password = serializers.CharField(style={"input_type": "password"},
#                                      write_only=True)
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username',
#                   'first_name', 'last_name', 'password')
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         return UsersSerializer(
#             instance.recipe,
#             context={'request': request}
#         ).data
#
#
# class UsersSerializer(UserSerializer):
# # class UsersSerializer(serializers.ModelSerializer):
#     avatar = Base64ImageField()
#     is_subscribed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'avatar',)
#
#     def get_is_subscribed(self, obj):
#
#         user = self.context.get('request').user
#         # followers = Follow.objects.filter(following=obj)
#         # return followers.filter(user=user).exists()
#         # if user.is_anonymous:
#         #     return False
#         return Follow.objects.filter(user=user, following=obj).exists()
#
#
#
#
# class UserAvatarSerializer(UsersSerializer):
#     class Meta:
#         model = User
#         fields = ('avatar', )
#
#
# # class FollowSerializer(serializers.ModelSerializer):
# #     """Сериализатор подписки на автора."""
# #     class Meta:
# #         model = Follow
# #
# #
# #
# # class FollowSerializer(serializers.ModelSerializer):
# # # # class FollowSerializer(UsersSerializer):
# #     """Сериализатор данных подписки/избранного."""
# #     email = serializers.ReadOnlyField(source='following.email')
# #     id = serializers.ReadOnlyField(source='following.id')
# #     username = serializers.ReadOnlyField(source='following.username')
# #     first_name = serializers.ReadOnlyField(source='following.first_name')
# #     last_name = serializers.ReadOnlyField(source='following.last_name')
# #     is_subscribed = serializers.SerializerMethodField()
# #     # avatar = serializers.ImageField(read_only=True, source='following.avatar')
# #     avatar = serializers.SerializerMethodField()
# #     recipies = serializers.SerializerMethodField()
# #     recipies_count = serializers.SerializerMethodField()
# #
# #     class Meta:
# #         model = Follow
# #         fields = ('email', 'id', 'username', 'first_name',
# #                   'last_name', 'is_subscribed', 'avatar', 'recipies',
# #                   'recipies_count')
# #
# #     def get_is_subscribed(self, obj):
# #         # user = self.context.get('request').user
# #         return Follow.objects.filter(
# #             user=obj.user, following=obj.following).exists()
# #         # pass
# # #
# #
# #     # def get_recipies(self, obj):
# #     #     request = self.context.get('request')
# #     #     limit = request.GET.get('recipes_limit')
# #     #     queryset = Recipies.objects.filter(author=obj.following)
# #     #     if limit:
# #     #         queryset = queryset[:int(limit)]
# #     #     return FavoriteShoppingShowSerializer(queryset, many=True).data
# # #         return Follow.objects.filter(
# # #             user=obj.user, following=obj.following).exists()
# # # #         return
# # # #
# # #
# #     def get_recipies_count(self, obj):
# #         # return obj.following.recipe_set.count()
# #         pass
# #
# #     def get_avatar(self, obj):
# # #         if obj.following.avatar:
# # #             return obj.following.avatar.url
# # #         return None
# #         pass
# # #         return
# # #     # def validate(self, data):
# # #     #     """Проверка данных перед подпиской."""
# # #     #     user = self.context.get('request').user
# # #     #     following = data.get('following')
# # #     #     current_subscription = Follow.objects.filter(user=user,
# # #     #                                                  following=following)
# # #     #     if following == user:
# # #     #         raise serializers.ValidationError(
# # #     #             'Нельзя подписаться на самого себя!'
# # #     #         )
# # #     #     if current_subscription:
# # #     #         raise serializers.ValidationError(
# # #     #             'Вы уже подписались на этого автора!'
# # #     #         )
# # #     #     return data
