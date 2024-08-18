from django.shortcuts import render
from djoser.views import UserViewSet
from.models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

