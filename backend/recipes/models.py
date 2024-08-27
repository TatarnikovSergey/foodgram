from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipies(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               related_name="recipies",
                               verbose_name='Автор')

