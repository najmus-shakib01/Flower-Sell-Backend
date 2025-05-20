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
from .models import Payment

class SSLCommerzFlowerPaymentView(APIView):
    def get(self, request, flower_id, *args, **kwargs):
        flower = get_object_or_404(Flower, id=flower_id)
        user = request.user
        
        existing_order = Order.objects.filter(
            user=user,
            flower=flower,
            status='Pending',
            transaction_id__isnull=True
        ).first()
        
        if existing_order:
            transaction_id = existing_order.transaction_id or str(uuid.uuid4())
            existing_order.transaction_id = transaction_id
            existing_order.save()
        else:
            transaction_id = str(uuid.uuid4())
            existing_order = Order.objects.create(
                user=user,
                flower=flower,
                quantity=1,
                status='Pending',
                transaction_id=transaction_id
            )
        
        sslcommerz_data = {
            'store_id': settings.SSL_COMMERZ['store_id'],
            'store_passwd': settings.SSL_COMMERZ['store_pass'],
            'total_amount': float(flower.price),
            'currency': 'BDT',
            'tran_id': transaction_id,
            'success_url': f"https://flower-sell-backend.vercel.app/api/v1/payment/payment_success/?order_id={existing_order.id}",
            'fail_url': f"https://flower-sell-backend.vercel.app/api/v1/payment/payment_fail/?order_id={existing_order.id}",
            'cus_name': user.username,
            'cus_email': user.email,
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
        
        return Response({'error': 'Payment initiation failed'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def payment_success(request, *args, **kwargs):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    order_id = request.GET.get('order_id')
    
    if tran_id and order_id:
        try:
            order = Order.objects.get(id=order_id, transaction_id=tran_id)
            order.status = 'Completed'
            print(order.status)
            order.save()
            
            Payment.objects.create(
                user=order.user,
                transaction_id=tran_id,
                amount=order.flower.price * order.quantity,
                status='Completed'
            )
            
            flower = order.flower
            flower.stock -= order.quantity
            flower.save()
            
            messages.success(request, "Payment successfully completed!")
        except Order.DoesNotExist:
            messages.error(request, "Order not found!")
    
    return redirect('https://flower-sell.vercel.app/order_history')


@csrf_exempt
def payment_fail(request, *args, **kwargs):
    print("Payment Fail GET Data:", request.GET)  
    flower_id = request.GET.get('id', None)  
    if flower_id:
        messages.error(request, "Payment failed! Please try again.")
        return redirect(f'https://flower-sell.vercel.app/flower_details/?flower_id={flower_id}')
    else:
        return redirect(f'https://flower-sell.vercel.app/flower_details/?flower_id={flower_id}')