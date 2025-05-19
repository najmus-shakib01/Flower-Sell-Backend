from django.db import models
from django.contrib.auth.models import User
import uuid

class Flower(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField()
    price = models.DecimalField(max_digits=11, decimal_places=2)
    image = models.CharField(default='', max_length=100)
    category = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.body[:50]}"

class PlantRevivalTip(models.Model):
    plant_name = models.CharField(max_length=255)
    symptoms = models.TextField()
    revival_steps = models.TextField()
    recommended_fertilizer = models.CharField(max_length=100)
    watering_caution = models.CharField(max_length=100)
    sunlight_adjustment = models.CharField(max_length=100)
    sunlight_needs = models.CharField(max_length=100)  
    recommended_water_frequency = models.CharField(max_length=100)  
    special_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revival Tips for {self.plant_name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_item')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.flower.title} - {self.quantity}'
