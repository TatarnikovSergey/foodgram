from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows anyone to perform read operations,
    but only staff users can perform write operations.
    """

    def has_permission(self, request, view):
        """
        Check if the request method is safe or if the user is authenticated and a staff member.
        """
        if request.method not in permissions.SAFE_METHODS and not (request.user.is_authenticated and request.user.is_staff):
            raise MethodNotAllowed(request.method)
        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the request method is safe or if the user is authenticated and a staff member.
        """
        if request.method not in permissions.SAFE_METHODS and not (request.user.is_authenticated and request.user.is_staff):
            raise MethodNotAllowed(request.method)
        return True




# from rest_framework import permissions
# from rest_framework import status
# from rest_framework.response import Response
#
#
# # class IsStaffOrReadOnly(permissions.BasePermission):
# #     """
# #     Пользователь должен быть персоналом, чтобы иметь право на отправку POST-запроса.
# #     Если пользователь не является персоналом, возвращается статус 405.
# #     """
# #     def has_permission(self, request, view):
# #         if request.method in permissions.SAFE_METHODS:
# #             if not request.user.is_staff:
# #                 return Response({"errors": "Теги нельзя добавить/изменить"},
# #                                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
# #         return True
# #
# class IsStaffOrReadOnly(permissions.BasePermission):
#     """
#     Пермишен полного доступа для персонала.
#     Позволяет только чтение другим пользователям,
#     а также чтение/изменение своего профиля.
#     При попытке изменения чужого контента возвращает статус 405"""
#
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or (
#                 request.user.is_authenticated
#                 and request.user.is_staff)
#         )
#
#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or (
#                 request.user.is_authenticated
#                 and request.user.is_staff)
#         )