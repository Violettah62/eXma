from django.urls import reverse
from rest_framework import status

from accounts.tests import BaseAPITestCase
from .models import Expense, ExpenseCategory


class ExpenseTestBase(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = ExpenseCategory.objects.create(name='Transport')

    def create_expense(self, employee, status_value=Expense.Status.DRAFT, amount='50.00'):
        return Expense.objects.create(
            employee=employee,
            category=self.category,
            amount=amount,
            description='Test expense',
            expense_date='2026-01-01',
            receipt='receipts/test.pdf',
            status=status_value,
        )


class RBACTests(ExpenseTestBase):

    def test_employee_cannot_create_user(self):
        self.login_as(self.employee)
        response = self.client.post(reverse('user-list'), {
            'email': 'newperson@test.com', 'first_name': 'New', 'last_name': 'Person',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        self.login_as(self.admin)
        response = self.client.post(reverse('user-list'), {
            'email': 'newperson@test.com', 'first_name': 'New', 'last_name': 'Person',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_approve_expense(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.PENDING)
        self.login_as(self.employee)
        response = self.client.post(reverse('expense-approve', args=[expense.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_approve_authorized_team_expense(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.PENDING)
        self.login_as(self.manager)
        response = self.client.post(reverse('expense-approve', args=[expense.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.status, Expense.Status.APPROVED)

    def test_finance_can_mark_approved_expense_paid(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.APPROVED)
        self.login_as(self.finance_officer)
        response = self.client.post(reverse('expense-mark-paid', args=[expense.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.status, Expense.Status.PAID)

    def test_auditor_cannot_modify_expense(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.DRAFT)
        self.login_as(self.auditor)
        response = self.client.patch(reverse('expense-detail', args=[expense.id]), {'amount': '999.00'})
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class ObjectLevelTests(ExpenseTestBase):

    def test_employee_cannot_access_other_employees_expense(self):
        """The single most important test per the spec: strict ownership isolation."""
        other_expense = self.create_expense(self.other_employee)
        self.login_as(self.employee)
        response = self.client.get(reverse('expense-detail', args=[other_expense.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WorkflowTests(ExpenseTestBase):

    def test_pending_to_approved_to_paid(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.PENDING)

        self.login_as(self.manager)
        response = self.client.post(reverse('expense-approve', args=[expense.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.status, Expense.Status.APPROVED)

        self.login_as(self.finance_officer)
        response = self.client.post(reverse('expense-mark-paid', args=[expense.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.status, Expense.Status.PAID)

    def test_pending_to_rejected(self):
        expense = self.create_expense(self.employee, status_value=Expense.Status.PENDING)
        self.login_as(self.manager)
        response = self.client.post(
            reverse('expense-reject', args=[expense.id]),
            {'comment': 'Missing receipt detail'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.status, Expense.Status.REJECTED)