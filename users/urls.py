from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegisterAPIView, UserProfileAPIView

urlpatterns = [
    path('auth/register/', UserRegisterAPIView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', UserProfileAPIView.as_view(), name='user-profile'),
]
