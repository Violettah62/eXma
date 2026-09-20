from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from audit.services import log_action
from .models import CustomUser, Department
from .permissions import IsAdministrator
from .serializers import UserCreateSerializer, UserSerializer, DepartmentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whoami(request):
    user = request.user
    return Response({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'department': user.department.name if user.department else None,
        'groups': list(user.groups.values_list('name', flat=True)),
        'is_superuser': user.is_superuser,
        'must_change_password': user.must_change_password,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    new_password = request.data.get('new_password')
    if not new_password:
        return Response({'detail': 'new_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(new_password, user=request.user)
    except DjangoValidationError as e:
        return Response({'detail': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new_password)
    request.user.must_change_password = False
    request.user.save()
    return Response({'detail': 'Password changed successfully.'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdministrator]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_action(
            request, 'user_created', 'CustomUser', user.id,
            f'{request.user.email} created user {user.email}.'
        )
        return Response(
            {
                'id': user.id,
                'email': user.email,
                'temporary_password': user._temp_password,
                'detail': 'User created successfully. Share this temporary password with the employee through a secure channel — it will not be shown again.',
            },
            status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(
            self.request, 'user_updated', 'CustomUser', instance.id,
            f'{self.request.user.email} updated user {instance.email}.'
        )

    def perform_destroy(self, instance):
        """'Delete' means deactivate — inactive users cannot authenticate, but their records (and audit trail) are preserved."""
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        log_action(
            self.request, 'user_deactivated', 'CustomUser', instance.id,
            f'{self.request.user.email} deactivated user {instance.email}.'
        )

    def perform_destroy(self, instance):
        """'Delete' means deactivate — inactive users cannot authenticate, but their records (and audit trail) are preserved."""
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdministrator()]
        return [IsAuthenticated()]
    
class LoggingTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get('email', '')
            try:
                user = CustomUser.objects.get(email=email)
                log_action(request, 'login', 'CustomUser', user.id, f'{email} logged in.', user=user)
            except CustomUser.DoesNotExist:
                pass
        return response