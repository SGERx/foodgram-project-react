from recipes.models import Ingredient, Recipe, Tag
from rest_framework import serializers
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'description', 'ingredients', 'tag')


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICE,
                                   default='user')

    class Meta:
        model = CustomUser
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  )
        required_fields = ('username', 'email')


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=30, required=True)
    username = serializers.CharField(max_length=30, required=True)

    def create(self, validated_data):

        return CustomUser.objects.create(**validated_data)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code',)