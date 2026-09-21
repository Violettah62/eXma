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
    the department of the employee associated with a given object.

    Works against any object that either IS a CustomUser, or HAS an
    'employee' attribute pointing to one (e.g. an Expense instance).
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        employee = getattr(obj, 'employee', obj)
        employee_department = getattr(employee, 'department', None)
        if employee_department is None:
            return False
        return employee_department.manager_id == request.user.id
    
class CanViewReports(BasePermission):
    """
    Finance Officers and Auditors get full access.
    Managers get access too, but views must further scope their
    results to the manager's own department(s) — this class only
    gates entry, it does not do that scoping itself.
    Administrators are deliberately NOT included here — per spec,
    they manage the system, not financial operations.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(
            name__in=['Finance Officer', 'Auditor', 'Manager']
        ).exists()
        
class IsAuditor(BasePermission):
    """Grants access only to users in the 'Auditor' group, or superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Auditor').exists()