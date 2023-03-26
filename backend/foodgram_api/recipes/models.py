from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_api import settings


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Name'
    )
    color = ColorField(
        format='hex', unique=True, verbose_name='Color'
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Name'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Measurement_unit'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
    )
    name = models.CharField(max_length=200, verbose_name='Name')
    text = models.TextField(
        verbose_name='Text', blank=True, null=True
    )
    image = models.ImageField(
        verbose_name='Image', upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientInRecipe', related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Time of cooking",
        validators=(
            MinValueValidator(
                1, message="Min tome of cooking - 1 min"
            ),
        ),
    )
    pub_date = models.DateTimeField('Date', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='ingredient_in_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Ingredients amount",
        default=1,
        validators=(
            MinValueValidator(
                1, message="Min tome of cooking - 1 min"
            ),
        ),
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Add ingredient to recipe'
        verbose_name_plural = 'Add ingredient to recipe'

    def __str__(self):
        return f'{self.ingredient.name}, {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Userь',
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='favorite',
    )
    favorite = models.BooleanField(verbose_name='Favorite', default=False)
    shopping_cart = models.BooleanField(
        verbose_name='Cooking cart', default=False
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'