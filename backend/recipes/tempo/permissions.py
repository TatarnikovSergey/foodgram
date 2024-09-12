from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ персоналу.
    Позволяет только чтение другим пользователям.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_staff)
        )