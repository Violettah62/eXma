from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import whoami, logout, create_user, change_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/whoami/', whoami, name='whoami'),
    path('api/logout/', logout, name='logout'),
    path('api/users/create/', create_user, name='create_user'),
    path('api/change-password/', change_password, name='change_password'),
]