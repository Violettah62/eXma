from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    """
    Grants access only to users in the 'Administrator' group,
    or Django superusers (who bypass group checks entirely).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Administrator').exists()