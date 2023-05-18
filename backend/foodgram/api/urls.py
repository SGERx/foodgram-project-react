from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, RecipeViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet)
router_v1.register('recipes', RecipeViewSet)

urlpatterns = [
    # path('auth/token/', get_token, name='token'),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
