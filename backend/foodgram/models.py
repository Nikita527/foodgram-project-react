from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Класс тэгов для рецептов."""

    name = models.CharField(
        'Тэг',
        max_length=settings.LENGTH_OF_FIELDS_RECIPE,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        db_index=False,
        validators=[
            RegexValidator(
                regex="^#(A-Fa-f0-9]|[A-Fa-f0-9]{3})$",
                message='Проверьте формат цвета',
            )
        ]
    )
    slug = models.SlugField(
        'Адрес Тэга',
        max_length=settings.LENGTH_OF_FIELDS_RECIPE,
        unique=True,
        db_index=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """Класс ингредиетов."""

    name = models.CharField(
        'Ингридиент',
        max_length=settings.LENGTH_OF_FIELDS_RECIPE,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=settings.LENGTH_OF_FIELDS_RECIPE,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Класс рецепты."""

    name = models.CharField(
        'Название',
        max_length=settings.LENGTH_OF_FIELDS_RECIPE,
        unique=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='AmountIngredient',
        related_name='recipes'
    )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='foodgram/'
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1, message='Время приготовления не менее 1 минуты!'
            ),
            MaxValueValidator(
                1441, message='Время приготовления не более 24 часов!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'


class AmountIngredient(models.Model):
    """Колличество ингредиентов используемых в блюде."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient_to_recipes',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe',)

    def __str__(self) -> str:
        return (
            f'{self.ingredient.name} - '
            f'{self.amount}'
            f' {self.ingredient.measurement_unit}'
        )


class FavoriteShoppingCart(models.Model):
    """Связывающая модель списка покупок и избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} :: {self.recipe}'


class Favorited(FavoriteShoppingCart):
    """Класс избранных рецептов."""

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorited'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Carts(FavoriteShoppingCart):
    """Рецепты в корзине покупок."""

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
