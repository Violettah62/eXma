from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import whoami, logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/whoami/', whoami, name='whoami'),
    path('api/logout/', logout, name='logout'),
]