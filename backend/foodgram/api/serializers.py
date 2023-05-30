import base64

from django.core.files.base import ContentFile
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser, Subscribtion

from .utils import recipe_ingredient_create


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = CustomUser
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribtion.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class IngredientRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount', 'recipe')


class RecipeFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Subscribtion
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def is_subscription_exists(self, obj):
        user = obj.user
        author = obj.author
        subscription_exists = Subscribtion.objects.filter(
            user=user, author=author).exists()
        return subscription_exists

    def retrieve_author_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit', None)
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serialized_data = RecipeFollowSerializer(queryset, many=True).data
        return serialized_data


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart',
                  'image')
        read_only_fields = ('id', 'author',)

    def is_recipe_favorited(self, obj):
        user = self.context['request'].user
        is_favorite = obj.favorites.filter(
            user=user).exists() if user.is_authenticated else False
        return is_favorite

    def is_recipe_in_cart(self, obj):
        user = self.context.get('request').user
        is_in_cart = user.shopping_cart.filter(
            recipe=obj).exists() if user.is_authenticated else False
        return is_in_cart

    def retrieve_recipe_ingredients(self, obj):
        recipe_ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        serialized_data = IngredientRecipeGetSerializer(
            recipe_ingredients, many=True).data
        return serialized_data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'image')
        read_only_fields = ('id', 'author', 'tags')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set(ingredient['id'] for ingredient in ingredients)
        if len(ingredients) > len(ingredients_set):
            raise serializers.ValidationError(
                'Проверьте, что ингредиент выбран не более одного раза.'
            )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe_ingredient_create(ingredients_data, IngredientInRecipe, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            amount_set = IngredientInRecipe.objects.filter(
                recipe=instance)
            amount_set.delete()
            recipe_ingredient_create(
                ingredients_data, IngredientInRecipe, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientRecipeGetSerializer(
            IngredientInRecipe.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        representation.pop('ingredients_data', None)
        representation.pop('tags_data', None)
        return representation
