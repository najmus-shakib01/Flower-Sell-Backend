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
        
        if Order.objects.filter(user=user, flower=flower, status='Completed').exists():
            return Response({'error': 'You have already purchased this flower.'}, status=status.HTTP_400_BAD_REQUEST)
            
        existing_order = Order.objects.filter(
            user=user,
            flower=flower,
            status='Pending'
        ).first()
        
        is_new_order = False
        if not existing_order:
            if flower.stock < 1:
                return Response({'error': 'Insufficient stock available'}, status=status.HTTP_400_BAD_REQUEST)
            existing_order = Order.objects.create(
                user=user,
                flower=flower,
                quantity=1,
                status='Pending',
                transaction_id=None  
            )
            flower.stock -= 1
            flower.save()
            is_new_order = True
        
        transaction_id = str(uuid.uuid4())
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        sslcommerz_data = {
            'store_id': settings.SSL_COMMERZ['store_id'],
            'store_passwd': settings.SSL_COMMERZ['store_pass'],
            'total_amount': float(flower.price),
            'currency': 'BDT',
            'tran_id': transaction_id,
            'success_url': f"{base_url}/api/v1/payment/payment_success/?order_id={existing_order.id}",
            'fail_url': f"{base_url}/api/v1/payment/payment_fail/?order_id={existing_order.id}",
            'cancel_url': f"{base_url}/api/v1/payment/payment_cancel/?order_id={existing_order.id}",
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

        try:
            response = requests.post(url, data=sslcommerz_data)

            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('status') == 'SUCCESS':
                    existing_order.transaction_id = transaction_id
                    existing_order.save()
                    return Response({'redirect_url': res_data['GatewayPageURL']}, status=status.HTTP_200_OK)
                
                if is_new_order:
                    flower.stock += 1
                    flower.save()
                    existing_order.delete()
                return Response({'error': 'Payment initiation failed', 'details': res_data}, status=status.HTTP_400_BAD_REQUEST)
            
            if is_new_order:
                flower.stock += 1
                flower.save()
                existing_order.delete()
            return Response({'error': 'Payment initiation failed', 'status_code': response.status_code, 'text': response.text}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            if is_new_order:
                flower.stock += 1
                flower.save()
                existing_order.delete()
            return Response({'error': f'Payment initiation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def payment_success(request, *args, **kwargs):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    order_id = request.GET.get('order_id')
    
    host = request.get_host()
    if '127.0.0.1' in host or 'localhost' in host:
        frontend_url = 'http://localhost:5173'
    else:
        frontend_url = 'https://flower-sell.vercel.app'
        
    if tran_id and order_id:
        try:
            order = Order.objects.get(id=order_id, transaction_id=tran_id)
            
            if order.status == 'Completed':
                messages.warning(request, "This order was already paid!")
                return redirect(f'{frontend_url}/order_history')
            
            order.status = 'Completed'
            order.save()
            
            if not Payment.objects.filter(transaction_id=tran_id).exists():
                Payment.objects.create(
                    user=order.user,
                    transaction_id=tran_id,
                    amount=order.flower.price * order.quantity,
                    status='Completed'
                )
            
            messages.success(request, "Payment successfully completed!")
        except Order.DoesNotExist:
            messages.error(request, "Order not found!")
    
    return redirect(f'{frontend_url}/order_history')


@csrf_exempt
def payment_fail(request, *args, **kwargs):
    order_id = request.GET.get('order_id')
    
    host = request.get_host()
    if '127.0.0.1' in host or 'localhost' in host:
        frontend_url = 'http://localhost:5173'
    else:
        frontend_url = 'https://flower-sell.vercel.app'
        
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'Pending'
            order.transaction_id = None
            order.save()

            messages.error(request, "Payment failed! Please try again.")
            return redirect(f'{frontend_url}/flower_details/?flower_id={order.flower.id}')
        
        except Order.DoesNotExist:
            messages.error(request, "Invalid order ID")
            return redirect(frontend_url)
    
    return redirect(f'{frontend_url}/auth_home')


@csrf_exempt
def payment_cancel(request, *args, **kwargs):
    order_id = request.GET.get('order_id')
    
    host = request.get_host()
    if '127.0.0.1' in host or 'localhost' in host:
        frontend_url = 'http://localhost:5173'
    else:
        frontend_url = 'https://flower-sell.vercel.app'
        
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'Pending'
            order.transaction_id = None
            order.save()

            messages.warning(request, "Payment canceled.")
            return redirect(f'{frontend_url}/flower_details/?flower_id={order.flower.id}')
        
        except Order.DoesNotExist:
            messages.error(request, "Invalid order ID")
            return redirect(frontend_url)
            
    return redirect(f'{frontend_url}/auth_home')