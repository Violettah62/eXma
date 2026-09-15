from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Department,CustomUser


@receiver(post_save, sender=Department)
def sync_manager_department(sender, instance, **kwargs):
    manager = instance.manager
    if manager and manager.department_id != instance.id:
        manager.department = instance
        manager.save(update_fields=['department'])

@receiver(post_save, sender=CustomUser)
def clear_stale_department_management(sender, instance, **kwargs):
    """
    A manager can only manage the department they currently belong to.
    If their own department changes, any OTHER department they were
    managing loses its manager automatically.
    """
    managed = instance.managed_departments.all()
    stale = managed.exclude(pk=instance.department_id) if instance.department_id else managed
    if stale.exists():
        stale.update(manager=None)