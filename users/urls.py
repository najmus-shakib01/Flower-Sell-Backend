from django.urls import path
from .views import (
    UserAPIView, RegisterAPIView, LoginAPIView, LogoutAPIView, VerifyOTPApiView, ResendOTPApiView
)

urlpatterns = [
    # user list and show
    path('user_all/', UserAPIView.as_view(), name='user-list'),  
    path('user_detail/<int:pk>/', UserAPIView.as_view(), name='user-detail'),  
    #user register and login and logout and active
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('resend_otp/', ResendOTPApiView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPApiView.as_view(), name='verify-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]