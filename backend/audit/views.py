from rest_framework import viewsets

from accounts.permissions import IsAuditor
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Auditor-only, read-only access. ReadOnlyModelViewSet only exposes
    list/retrieve — create, update, and delete aren't even routed,
    enforcing 'append-oriented' at the URL level, not just permissions.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditor]