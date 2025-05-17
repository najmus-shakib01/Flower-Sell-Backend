from rest_framework import serializers
from .models import Flower, Comment, PlantRevivalTip, CartItem
from django.contrib.auth.models import User
from .models import Comment
from users.models import Profile

class FlowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flower
        fields = ['id', 'title', 'description', 'price', 'image', 'category', 'stock']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  
        fields = ['id', 'username']


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 
    flower = serializers.PrimaryKeyRelatedField(queryset=Flower.objects.all())  
    profile_img = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'flower', 'body', 'created_on', 'profile_img']
        read_only_fields = ['user', 'created_on'] 

    def get_profile_img(self, obj):
        try:
            profile = Profile.objects.get(user=obj.user)  
            return profile.profile_img  
        except Profile.DoesNotExist:
            return None  

        
class CommentSerializer(serializers.Serializer):
    flowerId = serializers.IntegerField()
    comment = serializers.CharField(max_length=1000)
  
    class Meta:
        model = Comment
        fields = ['flowerId', 'user', 'comment']
        

class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'body'] 


class CommentCheckOrderSerializer(serializers.Serializer):
    flower_id = serializers.IntegerField(required=True)  
    

class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    message = serializers.CharField(max_length=1000)


class FlowerCareTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantRevivalTip
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    flower_price = serializers.DecimalField(source="flower.price", read_only=True, max_digits=10, decimal_places=2)
    flower_image = serializers.CharField(source="flower.image", read_only=True)
    flower_description = serializers.CharField(source="flower.description", read_only=True)
    flower_stock = serializers.IntegerField(source="flower.stock", read_only=True)
    flower_category = serializers.CharField(source="flower.category", read_only=True)
    flower = serializers.StringRelatedField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'flower', 'flower_price', 'flower_image', 'flower_description', 'flower_stock', 'flower_category', 'quantity', 'added_at']