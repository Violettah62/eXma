from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdministrator
from .models import ExpenseCategory, Expense
from .serializers import ExpenseCategorySerializer, ExpenseSerializer


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Administrators. Any authenticated user can list/view
    categories (needed so employees can pick one when submitting an
    expense), but only Administrators can create/edit/delete them.
    """
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrator()]
        return [IsAuthenticated()]


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Employees only ever see their own expenses. (Managers/Finance/
        Auditors get broader visibility, but that's built in later
        phases alongside their approval/reporting features.)
        """
        user = self.request.user
        if user.is_superuser:
            return Expense.objects.filter(is_deleted=False)
        return Expense.objects.filter(employee=user, is_deleted=False)

    def perform_destroy(self, instance):
        """Soft delete: never actually remove the row, per audit requirements."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    def update(self, request, *args, **kwargs):
        """Only draft expenses can be edited — once submitted, it's locked."""
        instance = self.get_object()
        if instance.status != Expense.Status.DRAFT:
            return Response(
                {'detail': 'Only draft expenses can be edited.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        expense = self.get_object()
        if expense.status != Expense.Status.DRAFT:
            return Response(
                {'detail': f'Cannot submit an expense with status "{expense.status}". Only drafts can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        expense.status = Expense.Status.PENDING
        expense.submitted_at = timezone.now()
        expense.save(update_fields=['status', 'submitted_at'])
        return Response(ExpenseSerializer(expense).data)