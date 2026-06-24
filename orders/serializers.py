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
    transaction_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'flower', 'price', 'quantity', 'status', 'order_date', 'transaction_id']
    
    def get_price(self, obj):
        return obj.flower.price

    def get_transaction_id(self, obj):
        if obj.status == 'Completed':
            return obj.transaction_id
        return None

class OrderSerializerForCreate(serializers.Serializer):
    user_id = serializers.IntegerField()
    flower = serializers.IntegerField()
    quantity = serializers.IntegerField()