from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
