from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ модераторам.
    Позволяет безопасные методы всем пользователям.
    """

    def has_permission(self, request, view):
        if (request.method not in permissions.SAFE_METHODS and not
           (request.user.is_authenticated and request.user.is_staff)):
            raise MethodNotAllowed(request.method)
        return True

    def has_object_permission(self, request, view, obj):
        if (request.method not in permissions.SAFE_METHODS and not
           (request.user.is_authenticated and request.user.is_staff)):
            raise MethodNotAllowed(request.method)
        return True


class IsAuthorOrModerPermission(permissions.BasePermission):
    """
    Разрешает доступ авторам объектов или модераторам.
    Позволяет безопасные методы всем пользователям.
    """

    def has_object_permission(self, request, view, obj):
        return any((
            request.method in permissions.SAFE_METHODS,
            obj.author == request.user,
            request.user.is_authenticated and request.user.is_staff
        ))