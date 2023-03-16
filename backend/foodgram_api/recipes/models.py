from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q

User = get_user_model()


MAX_LENGTH = 200
MAX_LENGTH_COLOR = 15


class Measure(models.Model):
    name = models.CharField(
        verbose_name='name', max_length=MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'measurement unit'
        verbose_name_plural = 'measurement unit'
        ordering = ('name',)

    def __str__(self):
        return self.name


class IngredientType(models.Model):
    name = models.CharField(
        verbose_name='name', max_length=MAX_LENGTH,
        db_index=True,
    )
    measurement_unit = models.ForeignKey(
        Measure,
        on_delete=models.PROTECT,
        related_name='ingredients',
        verbose_name='measurement unit'
    )

    class Meta:
        verbose_name = 'ingredients'
        verbose_name_plural = 'ingredients'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(fields=('name', 'measurement_unit'),
                                    name='unique_name_measurement_unit'),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='tag',
        max_length=MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug',
        max_length=MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Please use latin letters, numbers, signs _, -'
            ),
        ]
    )
    color = ColorField(
        verbose_name='tag color',
        max_length=MAX_LENGTH_COLOR,
        default="#ffffff"
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        ordering = ('pk',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='recipe name',
        max_length=MAX_LENGTH,
    )
    text = models.TextField(verbose_name='description')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author'
    )
    ingredient_types = models.ManyToManyField(
        IngredientType,
        verbose_name='type of ingredient',
        through='IngredientAmount'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='time of cooking in min',
        validators=[
            MinValueValidator(
                limit_value=1, message='Time of cooking can not be less than 1'
            )]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='tags',
    )
    favorited_by = models.ManyToManyField(
        User,
        verbose_name='favorite',
        related_name='favorited',
        blank=True
    )
    cart_of = models.ManyToManyField(
        User, verbose_name='cart',
        related_name='cart',
        blank=True
    )

    image = models.ImageField(
        upload_to='recipes/images/',
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='publication date')

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipe'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        IngredientType,
        on_delete=models.PROTECT,
        related_name='ingredient_amounts',
        verbose_name='ingredient type'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        validators=[
            MinValueValidator(
                limit_value=1, message='Amount can not be less than 1'
            )]
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe ingredient'
    )

    class Meta:
        verbose_name = 'ingredient in recipes'
        verbose_name_plural = 'ingredient in recipes'
        ordering = ('pk',)
        constraints = (
            models.UniqueConstraint(fields=('ingredient', 'recipe'),
                                    name='unique_ingredient_recipe'),
        )

    def __str__(self):
        return (f'{self.ingredient.name}, '
                f'{self.amount} {self.ingredient.measurement_unit}')


class Subscribe(models.Model):
    user = models.ForeignKey(User, related_name='subscribed_to',
                             on_delete=models.CASCADE,
                             verbose_name='subscriber')
    author = models.ForeignKey(User, related_name='subscribers',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'subscribe'
        verbose_name_plural = 'subscribes'
        constraints = (
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_user_author'),
            models.CheckConstraint(check=~Q(user=F('author')),
                                   name='author_not_user_constraint')
        )
        ordering = ('author__id',)

    def __str__(self):
        return f'{self.user.username}, {self.author.username}'