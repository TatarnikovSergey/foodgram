import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer

# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
# from .views import CustomUserViewSet

from .models import User, Follow


class Base64ImageField(serializers.ImageField):
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


# class UsersSerializer(UserSerializer):
class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)

    def get_is_subscribed(self, obj):

        user = self.context.get('request').user
        followers = Follow.objects.filter(following=obj)
        return followers.filter(user=user).exists()


class UserAvatarSerializer(UsersSerializer):
    class Meta:
        model = User
        fields = ('avatar', )


# class FollowSerializer(serializers.ModelSerializer):
#     """Сериализатор данных модели подписки."""
#
#     user = serializers.SlugRelatedField(read_only=True, slug_field='username')
#     following = serializers.SlugRelatedField(slug_field='username',
#                                              queryset=User.objects.all())
#
#     class Meta:
#         fields = ('user', 'following',)
#         model = Follow
#
#     def validate(self, data):
#         """Проверка данных перед подпиской."""
#         user = self.context.get('request').user
#         following = data.get('following')
#         current_subscription = Follow.objects.filter(user=user,
#                                                      following=following)
#         if following == user:
#             raise serializers.ValidationError(
#                 'Нельзя подписаться на самого себя!'
#             )
#         if current_subscription:
#             raise serializers.ValidationError(
#                 'Вы уже подписались на этого автора!'
#             )
#         return data
