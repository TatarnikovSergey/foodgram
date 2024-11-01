from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import MAX_LEN_EMAIL, MAX_LEN_NAME


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(max_length=MAX_LEN_EMAIL,
                              unique=True,
                              verbose_name='Адрес электронной почты')
    username = models.CharField(
        max_length=MAX_LEN_NAME, unique=True, verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='"username" содержит недопустимые символы.'
            )
        ]
    )
    first_name = models.CharField(max_length=MAX_LEN_NAME, verbose_name='Имя')
    last_name = models.CharField(max_length=MAX_LEN_NAME,
                                 verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='users/',
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


class Follow(models.Model):
    """Модель подписки на автора рецепта."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        verbose_name = 'Подписка на пользователей'
        verbose_name_plural = 'Подписки на пользователей'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow'
            ),)
