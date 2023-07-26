from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from django.shortcuts import get_object_or_404

from foodgram.models import (AmountIngredient, Carts, Favorites, Ingredient,
                             Prescription, Tag)
from users.models import User


class UserSerializer(UserSerializer):
    """Сериализатор для пользователей foodgram."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.subscriptions.filter(user=request.user).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей foodgram."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингридиентов в блюде."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class PrescriptionReadSerializer(serializers.ModelField):
    """Сериализатор для просмотра рецептов."""
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = AmountIngredientSerializer(
        many=True,
        source='ingredienttoprescription'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Prescription
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'description', 'cooking_time',)

    def get_ingredients(self, obj):
        ingredients = AmountIngredient.objects.filter(prescription=obj)
        return AmountIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()


class CreatePrescriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления новых рецептов."""
    ingredients = AmountIngredientSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тэга не существует'}
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Prescription
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'description', 'cooking_time',)

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тэга не существует'
                )
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 минуты'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте ингредиеты к блюду'
            )
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты можно добавлять только один раз'
                )
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Блюдо должно включать в себя хотя бы один ингредиент'
                )
            return ingredients

    @staticmethod
    def create_ingredients(prescription, ingredients):
        ingredients_list = []
        for ingredient_data in ingredients:
            ingredients_list.append(
                AmountIngredient(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    prescription=prescription,
                )
            )
        AmountIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        prescription = Prescription.objects.create(
            author=request.user, **validated_data
        )
        prescription.tags.set(tags)
        self.create_ingredients(prescription, ingredients)
        return prescription

    def update(self, instance, validated_data):
        instance.tags.clear()
        AmountIngredient.objects.filter(prescription=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return PrescriptionReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class PrescriptionShortSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов и покупок."""

    class Meta:
        model = Prescription
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorites
        fields = ('user', 'prescription',)

    def validate(self, data):
        user = data['user']
        if user.in_favorites.filter(prescription=data['prescription']).exists:
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        return data

    def to_representation(self, instance):
        return PrescriptionShortSerializer(
            instance.prescription,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = Carts
        fields = ('user', 'prescription',)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(
            prescription=data('prescription').exists()
        ):
            raise serializers.ValidationError(
                'Рецепт уже есть в корзине'
            )
        return data

    def to_representation(self, instance):
        return PrescriptionShortSerializer(
            instance.prescription,
            context={'request': self.context.get('request')}
        ).data


class SubscribeListSerializer(UserSerializer):
    """ Сериализатор для получения подписок """
    prescription_count = SerializerMethodField()
    prescription = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            UserSerializer.Meta.fields + ('prescription_count', 'prescription')
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_prescription_count(self, obj):
        return obj.prescription.count()

    def get_prescription(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('prescription_limit')
        prescription = obj.recipes.all()
        if limit:
            prescription = prescription[: int(limit)]
        serializer = PrescriptionShortSerializer(
            prescription, many=True, read_only=True
        )
        return serializer.data
