from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.is_admin))
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permossion(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin()
                or request.user.role == 'moderator'
                or obj.author == request.user)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == 'admin'
                or request.user.role == 'moderator'
                or obj.author == request.user)
