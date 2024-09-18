from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from .constants import (MAX_LEN_MEAS_UNIT, MAX_LEN_NAME, MAX_LEN_NAME_TAG,
                        MAX_LEN_SLUG)

User = get_user_model()


class Recipies(models.Model):
    """Модель рецептов."""
    tags = models.ManyToManyField('Tags',
                                  verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField('Ingredients',
                                         verbose_name='Ингредиент',
                                         through='IngredientsRecipies',)
    name = models.CharField(max_length=MAX_LEN_NAME,
                            verbose_name='Название')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(default=1,
                                       verbose_name='Время приготовления')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    is_favorite = models.ManyToManyField(User,
                                         through='Favorites',
                                         related_name='favorites_recipies',
                                         verbose_name='Избранный')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель Тегов."""
    name = models.CharField(max_length=MAX_LEN_NAME_TAG, unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True,
                            verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField(max_length=MAX_LEN_NAME, verbose_name='Название')
    measurement_unit = models.CharField(max_length=MAX_LEN_MEAS_UNIT,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Favorites(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipies, on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')
    constraints = [
        models.UniqueConstraint(fields=['user', 'recipe'],
                                name="unique_user_recipe")
    ]

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipies, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping_cart')
    constraints = [
        models.UniqueConstraint(fields=['user', 'recipe'],
                                name="unique_user_shopping_cart")
    ]

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class IngredientsRecipies(models.Model):
    """Модель связи рецепта и ингредиента."""
    recipe = models.ForeignKey(Recipies, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredients, models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        validators=(
            validators.MinValueValidator(
                1, message='Добавьте ингредиенты'),
        ),
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredients_recipe')
        ]
