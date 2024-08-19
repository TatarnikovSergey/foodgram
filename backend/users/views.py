from django.shortcuts import render
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from .models import User
from .serializers import UsersSerializer
from rest_framework import permissions


class CustomUserViewSet(UserViewSet):

    serializer_class = UsersSerializer
    # permission_classes = permissions.NOT

    def get_queryset(self):
        return User.objects.all()


