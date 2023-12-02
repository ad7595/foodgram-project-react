from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)

        if not has_permission:
            return False

        if request.user == view.author or request.user.is_staff:
            return True

        return request.method in SAFE_METHODS
