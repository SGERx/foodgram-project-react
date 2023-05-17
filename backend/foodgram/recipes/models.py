from django.db import models
from users.models import CustomUser


class Tag(models.Model):

    name = models.CharField(verbose_name='название',
                            max_length=16)
    hexcode = models.CharField(max_length=16)
    slug = models.CharField(unique=True,
                            max_length=16)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=16,
                            verbose_name='ингредиент')
    quantity = models.IntegerField()
    unit = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=16,
                            verbose_name='название')
    slug = models.CharField(unique=True,
                            max_length=16)
    author = models.ForeignKey(CustomUser, 
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='автор публикации')
    image = models.ImageField('Фотография',
                              upload_to='recipes/images/',
                              null=True,
                              default=None)
    description = models.TextField(verbose_name='текстовое описание')
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    related_name='recipes',
                                    verbose_name='ингредиент')
    tag = models.ForeignKey(Tag,
                            null=True,
                            on_delete=models.CASCADE,
                            related_name='recipes',
                            verbose_name='тег',
                            max_length=16)
    time = models.IntegerField()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name
