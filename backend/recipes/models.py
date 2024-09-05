from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipies(models.Model):
    """Модель рецептов."""
    tags = models.ManyToManyField('Tags', related_name='recipes', verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipies",
                               verbose_name='Автор')
    ingredients = models.ManyToManyField('Ingredients', related_name='recipes',
                                         verbose_name='Ингредиент')
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(default=1,
                                       verbose_name='Время приготовления')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель Тегов."""
    name = models.CharField(max_length=30, unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=30, unique=True,
                            verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField(max_length=60, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Favorites(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipies, on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipies,  on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class IngredientsRecipies(models.Model):
    """Модель связи рецепта и ингредиента."""
    recipe = models.ForeignKey(Recipies, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredients, models.CASCADE,
                                    verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredients_recipe')
            ]