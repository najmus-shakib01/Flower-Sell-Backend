from rest_framework import serializers
from .models import Order

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['flower', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    flower = serializers.StringRelatedField()
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'flower', 'price', 'quantity', 'status', 'order_date', 'transaction_id']
    
    def get_price(self, obj):
        return obj.flower.price

class OrderSerializerForCreate(serializers.Serializer):
    user_id = serializers.IntegerField()
    flower = serializers.IntegerField()
    quantity = serializers.IntegerField()