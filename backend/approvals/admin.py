from django.contrib import admin
from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('expense', 'reviewer', 'decision', 'reviewed_at')
    list_filter = ('decision',)
    search_fields = ('expense__description', 'reviewer__email')
    readonly_fields = ('reviewed_at',)