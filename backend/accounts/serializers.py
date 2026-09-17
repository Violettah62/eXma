import secrets
import string

from rest_framework import serializers
from .models import CustomUser, Department


def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'department']

    def create(self, validated_data):
        temp_password = generate_temp_password()
        user = CustomUser.objects.create_user(password=temp_password, **validated_data)
        user._temp_password = temp_password
        return user


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'department', 'department_name',
            'groups', 'is_active', 'is_staff', 'is_superuser', 'must_change_password',
            'date_joined',
        ]
        read_only_fields = ['id', 'is_superuser', 'must_change_password', 'date_joined', 'groups']


class DepartmentSerializer(serializers.ModelSerializer):
    manager_email = serializers.EmailField(source='manager.email', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager', 'manager_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']