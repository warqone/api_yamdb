from rest_framework.permissions import BasePermission


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin' or request.user.is_superuser is True:
            return True
