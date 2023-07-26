from django.contrib import admin
from django.contrib.admin import register

from .models import (AmountIngredient, Carts, Favorites, Ingredient,
                     Prescription, Tag)

EMTY_MSG = '-пусто-'


class IngridientInLine(admin.TabularInline):
    model = AmountIngredient
    extra = 3
    min_num = 1


@register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
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
        'prescription',
    )
    search_fields = (
        'user',
        'prescription',
    )
    list_filter = ('user', 'prescription',)
    empty_value_display = EMTY_MSG


@register(Carts)
class CartAdmin(admin.ModelAdmin):
    """Класс корзины покупок для админ панели."""
    list_display = (
        'user',
        'prescription',
    )
    search_fields = (
        'user',
        'prescription',
    )
    list_filter = ('user', 'prescription',)
    empty_value_display = EMTY_MSG
