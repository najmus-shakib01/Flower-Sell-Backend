from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Flower, Comment, CartItem, PlantRevivalTip
from orders.models import Order
from .serializers import (
    FlowerSerializer, CommentsSerializer, CommentCheckOrderSerializer,
    ContactFormSerializer, CommentEditSerializer, FlowerCareTipSerializer, CartItemSerializer
)
import logging
logger = logging.getLogger(__name__)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.mail import EmailMessage
import os

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

            subject = f"New message from {name} ({email})"
            email_message = f"""
            You have received a new message from your website:

            Name: {name}
            Email: {email}
            
            Message:
            {message}
            """
            from_email = os.environ.get("EMAIL")
           
            try:
                admin_email_obj = EmailMessage(
                    subject=subject,
                    body=email_message,
                    from_email=from_email,
                    to=[from_email],
                    reply_to=[email]
                )
                admin_email_obj.send(fail_silently=False)

                user_email_obj = EmailMessage(
                    subject="Flower Seal প্লাটফর্মের সাথে যোগাযোগের জন্য ধন্যবাদ!",
                    body=f"""হাই {name},\n\n
                    আমরা আপনার বার্তা পেয়েছি।\n\n
                    আপনার দেওয়া তথ্য :
                    নাম : {name}
                    ইমেইল : {email}
                    আপনার মেসেজটি ছিল : \n{message}""",
                    from_email=from_email,
                    to=[email]
                )
                user_email_obj.send(fail_silently=False)

                return Response({"message": "Email sent successfully! Please Check Your Email"}, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
                return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Flower Care Tips API
class FlowerCareTipAPIView(APIView):
    def get(self, request):
        tips = PlantRevivalTip.objects.all()
        serializer = FlowerCareTipSerializer(tips, many=True)
        return Response(serializer.data)


# Cart API
class CartApiView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        flower_id = request.data.get("flower")
        quantity = request.data.get("quantity", 1)  

        if not flower_id:
            return Response({"error": "Flower ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flower = Flower.objects.get(id=flower_id)
        except Flower.DoesNotExist:
            return Response({"error": "Flower not found"}, status=status.HTTP_404_NOT_FOUND)

        if CartItem.objects.filter(flower=flower, user=request.user).exists():
            return Response(
                {"error": "This product is already in your cart!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = CartItem.objects.create(
            user=request.user,
            flower=flower,
            quantity=quantity
        )
        
        serializer = CartItemSerializer(cart_item)
        return Response(
            {
                "message": "Product added to cart successfully!",
                "cart_item": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, cart_id):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            cart_item = CartItem.objects.get(id=cart_id, user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found or doesn't belong to you"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(
            {"message": "Item removed from cart successfully"},
            status=status.HTTP_200_OK
        )