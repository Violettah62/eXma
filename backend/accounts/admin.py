from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'department', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'department')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'department', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)