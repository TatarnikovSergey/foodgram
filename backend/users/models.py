from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=256, unique=True,
                              verbose_name='Адрес электронной почты')
    username = models.CharField(max_length=150, unique=True,
                                verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    password = models.CharField(max_length=150)
    avatar = models.ImageField(
        upload_to='media/users/',
        null=True,
        default=None,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
