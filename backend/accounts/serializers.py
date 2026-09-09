import secrets
import string

from rest_framework import serializers
from .models import CustomUser


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
        # Stash it on the instance so the view can return it once, right after creation.
        user._temp_password = temp_password
        return user