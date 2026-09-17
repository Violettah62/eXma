from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from accounts.permissions import IsAdministrator, IsManager, IsManagerOfEmployee, IsFinanceOfficer
from approvals.models import Approval
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
        user = self.request.user
        if user.is_superuser:
            return Expense.objects.filter(is_deleted=False)

        base = Expense.objects.filter(is_deleted=False)

        if user.groups.filter(name='Manager').exists() and hasattr(user, 'managed_departments'):
            managed_dept_ids = user.managed_departments.values_list('id', flat=True)
            return base.filter(
                models.Q(employee=user) | models.Q(employee__department_id__in=managed_dept_ids)
            )
            
        if user.groups.filter(name='Finance Officer').exists():
            return base.filter(
                models.Q(employee=user) | models.Q(status__in=[Expense.Status.APPROVED, Expense.Status.PAID])
            )

        return base.filter(employee=user)

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

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def approve(self, request, pk=None):
        expense = self.get_object()

        if not IsManagerOfEmployee().has_object_permission(request, self, expense):
            return Response(
                {'detail': 'You do not manage this employee\'s department.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if expense.status != Expense.Status.PENDING:
            return Response(
                {'detail': f'Cannot approve an expense with status "{expense.status}". Only pending expenses can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Approval.objects.create(
            expense=expense,
            reviewer=request.user,
            decision=Approval.Decision.APPROVED,
            comment=request.data.get('comment', ''),
        )
        expense.status = Expense.Status.APPROVED
        expense.save(update_fields=['status'])
        return Response(ExpenseSerializer(expense).data)

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def reject(self, request, pk=None):
        expense = self.get_object()

        if not IsManagerOfEmployee().has_object_permission(request, self, expense):
            return Response(
                {'detail': 'You do not manage this employee\'s department.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if expense.status != Expense.Status.PENDING:
            return Response(
                {'detail': f'Cannot reject an expense with status "{expense.status}". Only pending expenses can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = request.data.get('comment', '')
        if not comment.strip():
            return Response(
                {'detail': 'A comment explaining the rejection is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Approval.objects.create(
            expense=expense,
            reviewer=request.user,
            decision=Approval.Decision.REJECTED,
            comment=comment,
        )
        expense.status = Expense.Status.REJECTED
        expense.save(update_fields=['status'])
        return Response(ExpenseSerializer(expense).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsFinanceOfficer])
    def mark_paid(self, request, pk=None):
        expense = self.get_object()

        if expense.status != Expense.Status.APPROVED:
            return Response(
                {'detail': f'Cannot mark an expense with status "{expense.status}" as paid. Only approved expenses can be marked paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        expense.status = Expense.Status.PAID
        expense.save(update_fields=['status'])
        return Response(ExpenseSerializer(expense).data)