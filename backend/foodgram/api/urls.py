from django.urls import include, path
from rest_framework import routers

from .views import CustomUserCreateViewSet, CustomUserViewSet, get_token

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet)

urlpatterns = [
    path('v1/auth/signup/',
         CustomUserCreateViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/', include(router_v1.urls)),
]
