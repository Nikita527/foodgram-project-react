import django_filters as filters

from foodgram.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_list = filters.BooleanFilter(
        label='В корзине',
        method='filter_is_in_shopping_list'
    )
    is_favorites = filters.BooleanFilter(
        label='В избранных',
        method='filter_is_in_fovorites'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def filter_is_in_favorites(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_favorites__user=user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=user)
        return queryset
