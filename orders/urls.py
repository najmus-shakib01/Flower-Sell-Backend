from django.urls import path
from .views import OrderView, OrderAPIView, AllUsersOrderHistoryAPIView, UserOrderStatusAPIView, OneUserOrderStatsAPIView

urlpatterns = [
    path('create_order/', OrderView.as_view(), name='create-order'),
    path('my_order/', OrderAPIView.as_view(), name='my-orders'),
    path('all_order/', AllUsersOrderHistoryAPIView.as_view(), name='all-order'),
    path('user_order_stats/', UserOrderStatusAPIView.as_view(), name='user-order-stats'),
    path('one_user_order_stats/', OneUserOrderStatsAPIView.as_view(), name='user-order-stats'),
]