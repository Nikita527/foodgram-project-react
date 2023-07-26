import django_filters as filters

from django.core.exceptions import ValidationError

from foodgram.models import Ingredient, Prescription
from users.models import User


class TagsMultipleChoiceField(filters.fields.ModelMultipleChoiceField):
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
    field_class = TagsMultipleChoiceField


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class PrescriptionFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    in_carts = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В корзине'
    )
    in_fovorites = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В избранных'
    )
    tags = filters.AllValuesMultipleFilter(
        fields_name='tags__slug',
        label='Ссылка'
    )

    class Meta:
        model = Prescription
        fields = ['shopping_list', 'in_favorites', 'author', 'tags']
