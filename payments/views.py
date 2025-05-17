from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from flowers.models import Flower
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt
import requests

class SSLCommerzFlowerPaymentView(APIView):
    def get(self, request, flower_id, *args, **kwargs):
        flower = get_object_or_404(Flower, id=flower_id)
        transaction_id = str(uuid.uuid4())

        sslcommerz_data = {
            'store_id': settings.SSL_COMMERZ['store_id'],
            'store_passwd': settings.SSL_COMMERZ['store_pass'],
            'total_amount': float(flower.price),
            'currency': 'BDT',
            'tran_id': transaction_id,
            'success_url': f"https://flower-seal-backend.vercel.app/api/v1/payments/payment_success/",
            'fail_url': f"https://flower-seal-backend.vercel.app/api/v1/payments/payment_fail/?id={flower.id}",
            'cus_name': 'Test User',
            'cus_email': 'test@example.com',
            'cus_phone': '01700000000',
            'cus_add1': 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'product_name': flower.title,
            'product_category': flower.category,
            'product_profile': 'general',
        }

        url = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php' if settings.SSL_COMMERZ['issandbox'] \
            else 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'

        response = requests.post(url, data=sslcommerz_data)

        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('status') == 'SUCCESS':
                return Response({'redirect_url': res_data['GatewayPageURL']}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'SSLCommerz payment failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def payment_success(request, *args, **kwargs):
    print("Payment Success POST Data:", request.POST)  
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    if tran_id:
        order = Order.objects.filter(status='Pending', transaction_id=None).first()
        if order:
            order.status = 'Completed'
            print(order.status)
            order.transaction_id = tran_id  
            order.save()
            messages.success(request, "Payment successfully completed!")  
    return redirect('https://flower-sell.netlify.app/order_history')


@csrf_exempt
def payment_fail(request, *args, **kwargs):
    print("Payment Fail GET Data:", request.GET)  
    flower_id = request.GET.get('id', None)  
    if flower_id:
        messages.error(request, "Payment failed! Please try again.")
        return redirect(f'https://flower-sell.netlify.app/flower_details/?flower_id={flower_id}')
    else:
        return redirect('https://flower-sell.netlify.app/auth_home')