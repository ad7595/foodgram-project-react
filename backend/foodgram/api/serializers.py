from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    Tag, RecipeIngredient,
    ShoppingCart
    )
from users.models import Subscription


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
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
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        return ShortRecipeSerializer(
            recipes=obj.recipes.all()(author=obj.user), many=True,
            read_only=True).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

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
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                {"error": "Рецепт уже добавлен в избранное!"}
                )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance['recipe'],
            context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance['recipe'],
            context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time')


class RecipeIngredientsSerializer(serializers.ModelSerialize):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    # id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def create(self, validated_data):
        return RecipeIngredient.objects.create(
            ingredient=validated_data['id'],
            amount=validated_data['amount']
        )

    def validate_amount(self, data):
        if int(data) <= 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше или равно 1!'
            )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
            'is_in_shopping_cart',
            'is_favorited',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
            ).exists()


class RecipeCreateSerializer(serializers.ModelSerialize):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddRecipeIngredientsSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
        )

    def create_ingredients(self, ingredients, recipe):
        for i in ingredients:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(id=i['id']),
                recipe=recipe,
                amount=i['amount'],
            )

# проверить def validate

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for i in ingredients:
            ingredient_id = i['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'Вы уже использовали этот ингридиент!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] < 0:
            raise serializers.ValidationError(
                'Укажите время готовки!'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        recipe = Recipe.objects.create(**validated_data,
                                       author=self.context['request'].user)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data['ingredients']
        recipe = instance
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance['recipe'],
            context=self.context).data
