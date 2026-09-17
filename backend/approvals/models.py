from django.db import models

from accounts.models import CustomUser
from expenses.models import Expense


class Approval(models.Model):
    class Decision(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    expense = models.ForeignKey(
        Expense,
        on_delete=models.PROTECT,
        related_name='approvals',
    )
    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='reviews_given',
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return f'{self.reviewer.email} {self.decision} expense #{self.expense_id}'