from rest_framework import serializers
from .models import Approval


class ApprovalSerializer(serializers.ModelSerializer):
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)

    class Meta:
        model = Approval
        fields = ['id', 'expense', 'reviewer', 'reviewer_email', 'decision', 'comment', 'reviewed_at']
        read_only_fields = ['id', 'expense', 'reviewer', 'decision', 'reviewed_at']