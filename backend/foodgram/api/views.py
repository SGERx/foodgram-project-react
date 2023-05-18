from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.http import QueryDict
from django.shortcuts import get_object_or_404, render
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser

from .mixins import CreateListDestroyViewSet
from .permissions import CreateOrIsAuthorOrReadOnly, IsAdmin
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)
from .utils import create_code_and_send_email


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (CreateOrIsAuthorOrReadOnly)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # lookup_field = 'username'
    # # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username')
    # permission_classes = (IsAuthenticated, IsAdmin,)
    # http_method_names = ['get', 'post', 'patch', 'delete']

# class CustomUserCreateViewSet(mixins.CreateModelMixin,
#                               viewsets.GenericViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = SignupSerializer
#     permission_classes = (AllowAny,)

    # def create(self, request):
    #     data = request.data
    #     serializer = self.serializer_class(data=data)
    #     if isinstance(data, QueryDict):
    #         data = (request.data).dict()

    #     if CustomUser.objects.filter(**data).exists():
    #         user = CustomUser.objects.get(**data)
    #         create_code_and_send_email(user)

    #         return Response(serializer.initial_data,
    #                         status=status.HTTP_200_OK)

    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     create_code_and_send_email(user)

    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()



# @api_view(['POST'])
# @permission_classes([AllowAny])
# def get_token(request):
#     serializer = TokenSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     user = get_object_or_404(
#         CustomUser,
#         username=serializer.validated_data['username']
#     )
#     if not default_token_generator.check_token(
#         user,
#         serializer.validated_data['confirmation_code']
#     ):
#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     token = RefreshToken.for_user(user)
#     return Response(
#         {'token': str(token.access_token)},
#         status=status.HTTP_200_OK
#     )
