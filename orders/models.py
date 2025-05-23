from django.db import models
from django.contrib.auth.models import User
from flowers.models import Flower
from .constants import ORDER_STATUS
import uuid

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(choices=ORDER_STATUS, max_length=50, default='Pending')
    order_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f'{self.id} {self.user.username}'