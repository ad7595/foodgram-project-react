from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and request.user.follower.filter(
                author=obj
            ).exists()
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='author.id', required=False)
    email = serializers.EmailField(source='author.email', required=False)
    username = serializers.CharField(source='author.username', required=False)
    first_name = serializers.CharField(
        source='author.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='author.last_name',
        required=False
    )

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and Subscription.objects.filter(
                user=request.user, author=obj.author
            ).exists()
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = ShortRecipeSerializer(
            recipes,
            many=True,
            read_only=True,
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('name', 'amount', 'measurement_unit')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Рецепт уже добавлен в избранное!'}
            )
        return data

    def to_representation(self, obj):
        serializer = ShortRecipeSerializer(obj.recipe, context=self.context)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, obj):
        serializer = ShortRecipeSerializer(obj.recipe, context=self.context)
        return serializer.data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор карточки рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор связи рецепта и ингридиента."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингридиента в рецепт."""
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, data):
        if not data or len(data) <= 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше или равно 1!'
            )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddRecipeIngredientsSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'cooking_time',
            'ingredients',
            'tags',
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def validate_ingredients(self, ingredients):
        uniq_ingredients = set()

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in uniq_ingredients:
                raise serializers.ValidationError(
                    'Вы уже использовали этот ингридиент!'
                )
            uniq_ingredients.add(ingredient_id)
        return ingredients

    def validate_cooking_time(self, data):
        if data['cooking_time'] < 0:
            raise serializers.ValidationError('Укажите время готовки!')
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user,
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, obj, validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        recipe = obj
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        super().update(recipe, validated_data).save()

    def to_representation(self, obj):
        serializer = RecipeSerializer(obj, context=self.context)
        return serializer.data
