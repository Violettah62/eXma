from datetime import timedelta

from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import CanViewReports
from expenses.models import Expense


def get_scoped_queryset(user):
    """
    Returns the base Expense queryset this user is allowed to report on.
    Finance/Auditor/superusers: everything.
    Managers: only expenses from departments they manage.
    """
    base = Expense.objects.filter(is_deleted=False)

    if user.is_superuser:
        return base

    if user.groups.filter(name__in=['Finance Officer', 'Auditor']).exists():
        return base

    if user.groups.filter(name='Manager').exists():
        managed_dept_ids = user.managed_departments.values_list('id', flat=True)
        return base.filter(employee__department_id__in=managed_dept_ids)

    return base.none()


def apply_date_filter(queryset, request):
    """
    Supports ?period=today|week|month, or explicit ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD.
    No params at all means no filtering (all-time report).
    """
    period = request.query_params.get('period')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    now = timezone.now()

    if period == 'today':
        return queryset.filter(expense_date=now.date())
    elif period == 'week':
        start_of_week = now.date() - timedelta(days=now.weekday())
        return queryset.filter(expense_date__gte=start_of_week)
    elif period == 'month':
        return queryset.filter(expense_date__year=now.year, expense_date__month=now.month)
    elif start_date and end_date:
        return queryset.filter(expense_date__range=[start_date, end_date])

    return queryset

@api_view(['GET'])
@permission_classes([CanViewReports])
def expense_summary_report(request):
    queryset = apply_date_filter(get_scoped_queryset(request.user), request)

    summary = queryset.aggregate(
        total_count=Count('id'),
        total_amount=Sum('amount'),
    )

    by_status = {}
    for status_choice, _ in Expense.Status.choices:
        status_qs = queryset.filter(status=status_choice)
        by_status[status_choice] = {
            'count': status_qs.count(),
            'amount': status_qs.aggregate(total=Sum('amount'))['total'] or 0,
        }

    return Response({
        'total_count': summary['total_count'] or 0,
        'total_amount': summary['total_amount'] or 0,
        'by_status': by_status,
    })


@api_view(['GET'])
@permission_classes([CanViewReports])
def category_report(request):
    queryset = apply_date_filter(get_scoped_queryset(request.user), request)

    results = (
        queryset.values('category__name')
        .annotate(total_amount=Sum('amount'), count=Count('id'))
        .order_by('-total_amount')
    )

    return Response([
        {
            'category': row['category__name'],
            'total_amount': row['total_amount'] or 0,
            'count': row['count'],
        }
        for row in results
    ])


@api_view(['GET'])
@permission_classes([CanViewReports])
def department_report(request):
    queryset = apply_date_filter(get_scoped_queryset(request.user), request)

    results = (
        queryset.values('employee__department__name')
        .annotate(total_amount=Sum('amount'), count=Count('id'))
        .order_by('-total_amount')
    )

    return Response([
        {
            'department': row['employee__department__name'],
            'total_amount': row['total_amount'] or 0,
            'count': row['count'],
        }
        for row in results
    ])