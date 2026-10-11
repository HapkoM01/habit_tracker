from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnlyPublic(BasePermission):
    """CRUD только своих; публичные — только чтение."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and obj.is_public:
            return True
        return obj.user == request.user
