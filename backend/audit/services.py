from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, entity_type, entity_id, description, user=None):
    AuditLog.objects.create(
        user=user if user is not None else (request.user if request.user.is_authenticated else None),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=get_client_ip(request),
    )