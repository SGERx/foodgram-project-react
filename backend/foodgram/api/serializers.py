import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser, Subscription

from .permissions import IsAuthorOrReadOnly
from .utils import recipe_ingredient_create

User = get_user_model()

from django.contrib.auth import password_validation
from rest_framework import serializers


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True,
                                     validators=[password_validation.validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user



class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
                  'id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
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


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'name', 'image', 'cooking_time', 'author')


class SubscriptionSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True, source='author.id')
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.CharField(source='author.email', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj.author).exists()

    def validate(self, validated_data):
        author = validated_data.get('author')
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Вы уже подписаны на этого автора')
        subscription = Subscription.objects.create(author=author, user=user)
        return subscription

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeFollowSerializer(recipes, many=True, read_only=True)
        return serializer.data


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    permission_classes = (AllowAny, )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart',
                  'image')
        read_only_fields = ('id', 'author',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        is_favorite = obj.favorites.filter(
            user=user).exists() if user.is_authenticated else False
        return is_favorite

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        is_in_cart = user.shopping_cart.filter(
            recipe=obj).exists() if user.is_authenticated else False
        return is_in_cart

    def get_ingredients(self, obj):
        recipe_ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        serialized_data = IngredientInRecipeGetSerializer(
            recipe_ingredients, many=True).data
        return serialized_data


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeWriteSerializer(many=True)
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
        if 'text' in validated_data:
            text_data = validated_data.pop('text')
            instance.text = text_data
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientInRecipeGetSerializer(
            IngredientInRecipe.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        return representation
