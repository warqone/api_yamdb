from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin' or request.user.is_superuser is True:
            return True


class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser is True:
            return True
        return False


class ModeratorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'moderator':
            return True
        return False


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == 'admin'
                or request.user.role == 'moderator'
                or obj.author == request.user)