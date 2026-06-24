from django.urls import path
from .views import SSLCommerzFlowerPaymentView, payment_success, payment_fail, payment_cancel

urlpatterns = [
    path('payment_detail/<int:flower_id>/', SSLCommerzFlowerPaymentView.as_view(), name='sslcommerz_payment'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_fail/', payment_fail, name='payment_fail'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
]