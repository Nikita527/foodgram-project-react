import django_filters as filters

from django.core.exceptions import ValidationError

from foodgram.models import Ingredient, Recipe
from users.models import User


class TagsMultipleChoiceField(filters.fields.ModelMultipleChoiceField):
    """Фильтер для выбора тегов."""

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'],
                code='required'
            )
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )


class TagsFilter(filters.AllValuesMultipleFilter):
    """Фильтр тэгов."""

    field_class = TagsMultipleChoiceField


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    shopping_list = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В корзине'
    )
    in_favorites = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В избранных'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка'
    )

    class Meta:
        model = Recipe
        fields = ['shopping_list', 'in_favorites', 'author', 'tags']
