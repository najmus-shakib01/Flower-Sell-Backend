from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from .models import Flower, Comment, CartItem, PlantRevivalTip
from orders.models import Order
from .serializers import (
    FlowerSerializer, CommentsSerializer, CommentCheckOrderSerializer,
    ContactFormSerializer, CommentEditSerializer, FlowerCareTipSerializer, CartItemSerializer
)
import logging
logger = logging.getLogger(__name__)

# Flower API
class FlowerListAPIView(APIView):
    def get(self, request):
        flowers = Flower.objects.all()
        serializer = FlowerSerializer(flowers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FlowerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlowerDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Flower, pk=pk)

    def get(self, request, pk):
        flower = self.get_object(pk)
        serializer = FlowerSerializer(flower)
        return Response(serializer.data)

    def put(self, request, pk):
        flower = self.get_object(pk)
        serializer = FlowerSerializer(flower, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        flower = self.get_object(pk)
        flower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Comment API
class CommentAPIView(APIView):
    
    def post(self, request):
        serializer = CommentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Comment created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        
        if comment.user != request.user:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CommentShowAPIView(APIView):
    def get(self, request, flowerId):
        flower = get_object_or_404(Flower, id=flowerId)
        comments = Comment.objects.filter(flower=flower)
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)
    
class CommentEditAPIView(APIView):
    def get(self, request, postId):
        flower = get_object_or_404(Flower, id=postId)
        comments = Comment.objects.filter(flower=flower)
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)
    
    def put(self, request, commentId, *args, **kwargs):
        comment = get_object_or_404(Comment, id=commentId)
        serializer = CommentEditSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comment updated successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentCheckOrderAPIView(APIView):
    def get(self, request):
        print("Query Params:", request.query_params)  
        serializer = CommentCheckOrderSerializer(data=request.query_params)
        if serializer.is_valid():
            flower_id = serializer.validated_data['flower_id']
            print("Validated Flower ID:", flower_id)
            user = request.user
            flower = get_object_or_404(Flower, id=flower_id)
            order_exists = Order.objects.filter(user=user, flower=flower).exists()
            return Response({"can_comment": order_exists}, status=status.HTTP_200_OK)
        print("Serializer Errors:", serializer.errors)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Contact Form API
class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            message = serializer.validated_data['message']

            subject = f"Contact Form Submission from {name}"
            email_message = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

            try:
                send_mail(
                    subject,
                    email_message,
                    'noreply@yourdomain.com',
                    ['syednazmusshakib94@gmail.com'],
                    fail_silently=False,
                )
                return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Flower Care Tips API
class FlowerCareTipAPIView(APIView):
    def get(self, request):
        tips = PlantRevivalTip.objects.all()
        serializer = FlowerCareTipSerializer(tips, many=True)
        return Response(serializer.data)


# Cart API
class CartApiView(APIView):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        flower_id = request.data.get("flower")
        quantity = request.data.get("quantity")

        if not flower_id or not quantity:
            return Response({"error": "Missing flower or quantity data"}, status=status.HTTP_400_BAD_REQUEST)

        flower = get_object_or_404(Flower, id=flower_id)
        existing_item = CartItem.objects.filter(flower=flower, user=request.user).first()
        if existing_item:
            return Response({"error": "This Product Is Already In Your Cart!"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartItem.objects.create(user=request.user, flower=flower, quantity=quantity)
        return Response({"message": "Product Added Successfully!", "cart_item": cart_item.id}, status=status.HTTP_201_CREATED)

    def delete(self, request, cart_id):
        cart_item = get_object_or_404(CartItem, id=cart_id, user=request.user)
        cart_item.delete()
        return Response({"message": "Item Removed From Cart Successfully"}, status=status.HTTP_200_OK)