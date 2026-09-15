from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    """Grants access only to users in the 'Administrator' group, or superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Administrator').exists()


class IsManager(BasePermission):
    """Grants access only to users in the 'Manager' group, or superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Manager').exists()


class IsFinanceOfficer(BasePermission):
    """Grants access only to users in the 'Finance Officer' group, or superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Finance Officer').exists()


class IsAuditor(BasePermission):
    """Grants access only to users in the 'Auditor' group, or superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Auditor').exists()


class IsManagerOfEmployee(BasePermission):
    """
    Object-level permission: grants access only if request.user manages
    the department that a given employee (obj) belongs to.

    Use this alongside IsManager on views where a Manager acts on a
    SPECIFIC employee or their data (e.g. approving one person's expense),
    not just "is this user a Manager in general."
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        employee_department = getattr(obj, 'department', None)
        if employee_department is None:
            return False
        return employee_department.manager_id == request.user.id