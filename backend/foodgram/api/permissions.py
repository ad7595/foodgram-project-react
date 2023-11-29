# from rest_framework.permissions import SAFE_METHODS, BasePermission


# class IsAuthorOrAdminOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         return True

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in SAFE_METHODS
#             or obj.author == request.user
#             or request.user.is_staff
# )

from rest_framework.permissions import IsAuthenticated


class IsAuthorOrAdminOrReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        # вызываем родительский метод, чтобы проверить аутентификацию
        has_permission = super().has_permission(request, view)

        if not has_permission:
            return False

        # проверяем, является ли пользователь автором или администратором
        if request.user == view.author or request.user.is_staff:
            return True

        # в остальных случаях разрешаем только чтение
        return request.method in SAFE_METHODS
