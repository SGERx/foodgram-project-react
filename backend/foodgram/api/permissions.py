from django.contrib.auth import get_user_model
from rest_framework.permissions import SAFE_METHODS, BasePermission

User = get_user_model()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):

        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):

        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class CreateOrIsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):

        return (
            (request.user.is_anonymous
             and request.method in SAFE_METHODS)
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moder
            or request.user == obj.author
        )
