from venv import logger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order
from flowers.models import Flower
from .serializers import OrderSerializer, OrderCreateSerializer
from .constants import PENDING, COMPLETED
from .models import Order
from .serializers import OrderSerializer
import logging
import uuid
logger = logging.getLogger(__name__)
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, F
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated

#eta hocce flower order korar jonno post and get
class OrderAPIView(APIView): 
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#eta hocce order history dekar jonno and order view dekar jonno and flower kinar pore email jabe and flower buy korle quentity kome jabe
class OrderView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            flower_id = serializer.validated_data['flower'].id  
            quantity = serializer.validated_data['quantity']
            flower = get_object_or_404(Flower, id=flower_id)  

            if flower.stock < quantity:
                return Response({'error': 'Insufficient stock available'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Order.objects.create(
                    user=request.user,
                    flower=flower,
                    quantity=quantity,
                    status='Pending',  
                    transaction_id=None
                )
                flower.stock -= quantity
                flower.save()

                subject = "Thank You For Your Order!"
                message = f"""
                Dear {user.username}

                Your order has been successfully placed. Here are the details :

                -Product : {flower.title}
                -Quantity : {quantity}
                -Order Id : {order.id}

                We will notify you once your order is shipped.

                Thank you for shopping with us!
                """ 

                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

                return Response({'status': 'Order Placed Successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating order: {e}")
                return Response({'error': 'Order creation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AllUsersOrderHistoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

#one user order data
class OneUserOrderStatsAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        total_orders = Order.objects.filter(user=user).count()

        completed_payment = Order.objects.filter(user=user, status='Completed').count()

        pending_payment = Order.objects.filter(user=user, status='Pending').count()

        total_payment_amount = Order.objects.filter(user=user, status='Completed').aggregate(total=Sum('flower__price'))['total'] or Decimal('0.00')

        total_order_amount = Order.objects.filter(user=user).aggregate(total=Sum('flower__price'))['total'] or Decimal('0.00')

        data = {
            'Total_Orders': total_orders,
            'Completed_Payments': completed_payment,
            'Pending_Payments': pending_payment,
            'Total Payments Amount': total_payment_amount,
            'Total Order Amount': total_order_amount,
        }

        return Response(data, status=status.HTTP_200_OK)

#all user order data
class UserOrderStatusAPIView(APIView):

    def get(self, request, *args, **kwargs):

        total_orders = Order.objects.count()

        comopleted_payment = Order.objects.filter(status='Completed').count()

        pending_payment = Order.objects.filter(status='Pending').count()

        total_payment_amount = Order.objects.filter(status='Completed').aggregate(total=Sum('flower__price'))['total'] or Decimal('0.00')

        total_order_amount = Order.objects.filter().aggregate(total=Sum('flower__price'))['total'] or Decimal('0.00')

        total_profit = total_payment_amount * Decimal('0.10')

        data = {
            'Total_Orders' : total_orders,
            'Completed_Payments' : comopleted_payment,
            'Pending_Payments' : pending_payment,
            'Total Payments Amount' : total_payment_amount,
            'Total Order Amount': total_order_amount,
            'Total Profit' : total_profit
        }

        return Response(data, status=status.HTTP_200_OK)