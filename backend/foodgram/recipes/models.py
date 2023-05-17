from django.db import models
from users.models import CustomUser


class Tag(models.Model):

    name = models.CharField(verbose_name='название',
                            max_length=16)
    color = models.CharField(max_length=16)
    slug = models.CharField(unique=True,
                            max_length=16)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=16,
                            verbose_name='ингредиент')
    quantity = models.IntegerField()
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    related_name='recipes',
                                    verbose_name='ингредиент')
    tags = models.ForeignKey(Tag,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='recipes',
                             verbose_name='тег',)
    image = models.ImageField('Фотография',
                              upload_to='recipes/images/',
                              null=True,
                              default=None)
    name = models.CharField(max_length=200,
                            verbose_name='название')
    text = models.TextField(verbose_name='описание')
    cooking_time = models.IntegerField(
        verbose_name='время приготовления в минутах', min_value=1)
    slug = models.CharField(unique=True,
                            max_length=16)
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='автор публикации')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name
