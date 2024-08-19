from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
# from .views import CustomUserViewSet

from .models import User


class CreateUserSerializer(UserCreateSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True)
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class UsersSerializer(UserSerializer):
# class UsersSerializer(serializers.ModelSerializer):

    queryset = User.objects.all()

    class Meta:

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)
