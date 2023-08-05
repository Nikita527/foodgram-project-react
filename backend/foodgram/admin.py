from django.contrib import admin
from django.contrib.admin import register

from .models import AmountIngredient, Carts, Favorites, Ingredient, Recipe, Tag

EMTY_MSG = '-пусто-'


class IngridientInLine(admin.TabularInline):
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
        'get_favorites',
        'get_ingridients',
        'pub_date',
    )
    search_fields = (
        'name',
        'author',
        'tags',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    inlines = (IngridientInLine,)
    empty_value_display = EMTY_MSG

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = (
            qs.select_related('author')
            .prefetch_related('tags__tag', 'ingredients__ingredient')
        )
        return qs

    def get_favorites(self, obj):
        return obj.in_favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingridients(self, obj):
        return ', '.join([
            ingridients.name for ingridients
            in obj.ingridients.all()
        ])
    get_ingridients.short_description = 'Ингридиеты'


@register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    """Класс ингридиетов для админ панели."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
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


@register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Класс избранных рецептов для админ панели."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe',)
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
    list_filter = ('user', 'recipe',)
    empty_value_display = EMTY_MSG

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('author', 'recipe')
        return qs
