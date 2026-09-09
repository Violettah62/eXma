from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdministrator
from .serializers import UserCreateSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


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
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_205_RESET_CONTENT
        )
    except Exception:
        return Response(
            {'detail': 'Invalid or expired token.'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAdministrator])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'id': user.id,
                'email': user.email,
                'temporary_password': user._temp_password,
                'detail': 'User created successfully. Share this temporary password with the employee through a secure channel — it will not be shown again.',
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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