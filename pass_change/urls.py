from django.urls import path
from .views import PasswordChangeAPIView, PasswordResetRequestAPIView

urlpatterns = [
    path('password_reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('reset_password/<uid64>/<token>/', PasswordChangeAPIView.as_view(), name='password-change'),
]