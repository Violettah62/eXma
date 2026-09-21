from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'entity_type', 'entity_id', 'description', 'ip_address', 'created_at']
        read_only_fields = fields