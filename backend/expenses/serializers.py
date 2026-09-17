from rest_framework import serializers
from .models import ExpenseCategory, Expense


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSerializer(serializers.ModelSerializer):
    employee_email = serializers.EmailField(source='employee.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'employee', 'employee_email', 'category', 'category_name',
            'amount', 'description', 'expense_date', 'receipt', 'status',
            'is_deleted', 'submitted_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee', 'status', 'is_deleted', 'submitted_at', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError('This category is not active and cannot be used.')
        return value

    def validate_description(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError('Description must be at least 5 characters long.')
        return value

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)