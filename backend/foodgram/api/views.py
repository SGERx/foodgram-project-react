import datetime
import io

from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import FileResponse, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import DEFAULT_FROM_EMAIL
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser, Subscribtion

from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateListDestroyViewSet, ListRetrieveViewSet
from .pagination import CustomPagination
from .permissions import (CreateOrIsAuthorOrReadOnly, IsAdmin,
                          IsAdminOrReadOnly, IsAuthorOrReadOnly)
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeFollowSerializer, RecipeGetSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(['get'], detail=False)
    def me(self, request):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(CustomUser, pk=pk)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'author': author.pk}, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribtion, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscribtions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')

        if is_favorited is not None and int(is_favorited) == 1:
            return queryset.filter(favorites__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
            return queryset.filter(cart__user=self.request.user)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response('Рецепт успешно удален',
                        status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action != 'create':
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'],)
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            return post(request, pk, Favorite, RecipeFollowSerializer)
        return delete(request, pk, Favorite)

    @action(detail=True, methods=['POST', 'DELETE'],)
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return post(request, pk, ShoppingCart, RecipeFollowSerializer)
        return delete(request, pk, ShoppingCart)


class ShoppingCardView(APIView):
    def get(self, request):
        user = request.user
        shopping_list = (IngredientInRecipe.objects
                        .filter(recipe__cart__user=user)
                        .values('ingredient__name', 'ingredient__measurement_unit')
                        .annotate(amount=Sum('amount'))
                        .order_by())

        font = 'Tantular'
        pdfmetrics.registerFont(TTFont('Tantular', 'Tantular.ttf', 'UTF-8'))

        buffer = io.BytesIO()
        pdf_file = canvas.Canvas(buffer)

        pdf_file.setPageSize((595.27, 841.89))

        pdf_file.setFont(font, 24)
        pdf_file.drawString(150, 770, 'Shopping list:')
        pdf_file.setFont(font, 14)

        from_bottom = 750
        for number, ingredient in enumerate(shopping_list, start=1):
            ingredient_name = ingredient['ingredient__name']
            amount = ingredient['amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            line = f"{number}. {ingredient_name} - {amount} {measurement_unit}"
            pdf_file.drawString(50, from_bottom, line)
            from_bottom -= 20

            if from_bottom <= 50:
                from_bottom = 800
                pdf_file.showPage()
                pdf_file.setFont(font, 14)

        pdf_file.showPage()
        pdf_file.save()

        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_list.pdf'
        )


def post(request, pk, model, serializer):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            {'errors': 'Рецепт уже есть в избранном/списке покупок'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    model.objects.create(user=user, recipe=recipe)
    serialized_recipe = serializer(recipe).data
    return Response(serialized_recipe, status=status.HTTP_201_CREATED)


def delete(request, pk, model):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if model.objects.filter(user=user, recipe=recipe).exists():
        follow = get_object_or_404(model, user=user, recipe=recipe)
        follow.delete()
        return Response(
            'Рецепт успешно удален из избранного/списка покупок',
            status=status.HTTP_204_NO_CONTENT
        )
    return Response(
        {'errors': 'Рецепта не было в избранном/списке покупок'},
        status=status.HTTP_400_BAD_REQUEST
    )


def create_code_and_send_email(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Добро пожаловать на проект Foodgram!',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=(user.email,),
        message=confirmation_code,
        fail_silently=False
    )
