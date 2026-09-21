from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reports.views import expense_summary_report, category_report, department_report
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import LoggingTokenObtainPairView
from audit.views import AuditLogViewSet

from accounts.views import whoami, logout, change_password, UserViewSet, DepartmentViewSet
from expenses.views import ExpenseCategoryViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'categories', ExpenseCategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'users', UserViewSet, basename='user')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', LoggingTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/whoami/', whoami, name='whoami'),
    path('api/logout/', logout, name='logout'),
    path('api/change-password/', change_password, name='change_password'),
    path('api/', include(router.urls)),
    path('api/reports/summary/', expense_summary_report, name='expense_summary_report'),
    path('api/reports/by-category/', category_report, name='category_report'),
    path('api/reports/by-department/', department_report, name='department_report'),
]

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)