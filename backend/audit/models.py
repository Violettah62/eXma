from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        USER_CREATED = 'user_created', 'User Created'
        USER_UPDATED = 'user_updated', 'User Updated'
        USER_DEACTIVATED = 'user_deactivated', 'User Deactivated'
        ROLE_ASSIGNED = 'role_assigned', 'Role Assigned'
        EXPENSE_CREATED = 'expense_created', 'Expense Created'
        EXPENSE_UPDATED = 'expense_updated', 'Expense Updated'
        EXPENSE_SUBMITTED = 'expense_submitted', 'Expense Submitted'
        EXPENSE_DELETED = 'expense_deleted', 'Expense Deleted'
        EXPENSE_APPROVED = 'expense_approved', 'Expense Approved'
        EXPENSE_REJECTED = 'expense_rejected', 'Expense Rejected'
        EXPENSE_MARKED_PAID = 'expense_marked_paid', 'Expense Marked Paid'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} by {self.user} on {self.entity_type} #{self.entity_id}'