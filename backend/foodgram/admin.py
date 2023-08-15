from django.contrib import admin
from django.contrib.admin import register

from .models import AmountIngredient, Carts, Favorited, Ingredient, Recipe, Tag

EMTY_MSG = '-пусто-'


class IngredientInLine(admin.TabularInline):
    """Класс для правильного отображения количества ингредиетов."""

    model = AmountIngredient
    extra = 3
    min_num = 1


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс рецептов для админ панели."""

    list_display = (
        'author',
        'name',
        'cooking_time',
        'get_favorited',
        'get_ingredients',
        'pub_date',
    )
    search_fields = (
        'name',
        'author',
    )
    list_filter = (
        'author',
        'tags',
    )
    inlines = (IngredientInLine,)
    empty_value_display = EMTY_MSG

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = (
            qs.select_related('author')
            .prefetch_related('tags', 'ingredients')
        )
        return qs

    def get_favorited(self, obj):
        return obj.favorited.count()
    get_favorited.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()
        ])
    get_ingredients.short_description = 'Ингридиеты'


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс ингридиетов для админ панели."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = EMTY_MSG


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс тэгов для админ панели."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'slug',)
    list_filter = ('name',)
    empty_value_display = EMTY_MSG


@register(Favorited)
class FavoritedAdmin(admin.ModelAdmin):
    """Класс избранных рецептов для админ панели."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    empty_value_display = EMTY_MSG

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('user', 'recipe')
        return qs


@register(Carts)
class CartAdmin(admin.ModelAdmin):
    """Класс корзины покупок для админ панели."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    empty_value_display = EMTY_MSG

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('user', 'recipe')
        return qs
