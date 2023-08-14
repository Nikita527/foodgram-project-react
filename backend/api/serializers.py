import base64

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404

from foodgram.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Класс для кодирования картинок перед загрузкой."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей foodgram."""

    class Meta:
        model = User
        fields = (
            'id',
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

    id = serializers.IntegerField(write_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorites = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_list = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorites', 'is_in_shopping_list',
                  'name', 'image', 'text', 'cooking_time',)

    def get_ingredients(self, obj):
        ingredients = AmountIngredient.objects.filter(recipe=obj)
        return AmountIngredientSerializer(ingredients, many=True).data

    def get_is_favorites(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return (
            Recipe.objects.filter(in_favorites__user=user, id=obj.id).exists()
        )

    def get_is_in_shopping_list(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return (
            Recipe.objects.filter(shopping_list__user=user, id=obj.id).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления новых рецептов."""

    ingredients = AmountIngredientSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text',
                  'cooking_time',)

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один тэг'
            )
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 минуты'
            )
        return cooking_time

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                AmountIngredient(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    amount=ingredient.pop('amount'),
                    recipe=recipe,
                )
            )
        AmountIngredient.objects.bulk_create(ingredient_list)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=request.user, **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        AmountIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов и покупок."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeListSerializer(UserSerializer):
    """Сериализатор для получения подписок."""

    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            UserSerializer.Meta.fields + ('recipes',)
        )
        read_only_fields = ('email', 'username',)

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

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data
