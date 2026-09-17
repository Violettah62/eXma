from django.contrib import admin
from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'category', 'amount', 'status', 'expense_date', 'is_deleted')
    list_filter = ('status', 'category', 'is_deleted')
    search_fields = ('employee__email', 'description')
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')