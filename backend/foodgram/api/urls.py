from api.views import SubscriptionListView, SubscriptionView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('users/subscriptions/',
         SubscriptionListView.as_view(),
         name='subscriptions'),
    path('users/<int:user_id>/subscribe/',
         SubscriptionView.as_view(),
         name='subscribe'),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/set_password/', UserViewSet.as_view(), name='set_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
