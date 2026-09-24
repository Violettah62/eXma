from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Department
from django.urls import reverse
from rest_framework import status


class BaseAPITestCase(APITestCase):
    """
    Shared fixtures for every test module: departments, the five RBAC
    groups, and one user per role, already assigned to their group and
    department. Subclasses just call self.login_as(user) to authenticate.
    """

    @classmethod
    def setUpTestData(cls):
        cls.dept_it = Department.objects.create(name='IT')
        cls.dept_ops = Department.objects.create(name='Operations')

        cls.group_admin = Group.objects.create(name='Administrator')
        cls.group_manager = Group.objects.create(name='Manager')
        cls.group_finance = Group.objects.create(name='Finance Officer')
        cls.group_auditor = Group.objects.create(name='Auditor')
        cls.group_employee = Group.objects.create(name='Employee')

        cls.dept_it.manager = None  # set below, after the manager user exists

        cls.admin = CustomUser.objects.create_user(
            email='admin@test.com', password='TestPass123!', first_name='Admin', last_name='User',
            department=cls.dept_it,
        )
        cls.admin.groups.add(cls.group_admin)

        cls.manager = CustomUser.objects.create_user(
            email='manager@test.com', password='TestPass123!', first_name='Manager', last_name='User',
            department=cls.dept_it,
        )
        cls.manager.groups.add(cls.group_manager)
        cls.dept_it.manager = cls.manager
        cls.dept_it.save()

        cls.employee = CustomUser.objects.create_user(
            email='employee@test.com', password='TestPass123!', first_name='Employee', last_name='One',
            department=cls.dept_it,
        )
        cls.employee.groups.add(cls.group_employee)

        cls.other_employee = CustomUser.objects.create_user(
            email='other@test.com', password='TestPass123!', first_name='Employee', last_name='Two',
            department=cls.dept_ops,
        )
        cls.other_employee.groups.add(cls.group_employee)

        cls.finance_officer = CustomUser.objects.create_user(
            email='finance@test.com', password='TestPass123!', first_name='Finance', last_name='User',
            department=cls.dept_ops,
        )
        cls.finance_officer.groups.add(cls.group_finance)

        cls.auditor = CustomUser.objects.create_user(
            email='auditor@test.com', password='TestPass123!', first_name='Auditor', last_name='User',
            department=cls.dept_ops,
        )
        cls.auditor.groups.add(cls.group_auditor)

    def login_as(self, user):
        """Skips the HTTP login round-trip; generates a valid token directly."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
class AuthenticationTests(BaseAPITestCase):

    def test_valid_login_returns_tokens(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'employee@test.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login_wrong_password_is_rejected(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'employee@test.com',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_cannot_login(self):
        self.employee.is_active = False
        self.employee.save()
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'employee@test.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_returns_new_access_token(self):
        login_response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'employee@test.com',
            'password': 'TestPass123!',
        })
        refresh_token = login_response.data['refresh']
        response = self.client.post(reverse('token_refresh'), {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_unauthorized_request_is_rejected(self):
        response = self.client.get(reverse('whoami'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)