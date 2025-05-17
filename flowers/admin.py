from django.contrib import admin
from .models import Flower, Comment, PlantRevivalTip, CartItem

class FlowerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'price', 'image', 'category', 'stock']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'body', 'user', 'created_on']

class FlowerCareTipAdmin(admin.ModelAdmin):
    list_display = ['id', 'plant_name','symptoms','revival_steps','recommended_fertilizer','watering_caution','sunlight_adjustment', 'sunlight_needs', 'recommended_water_frequency','created_at', 'updated_at']

class CartFlowerItem(admin.ModelAdmin):
    list_display = ['id', 'user', 'flower', 'added_at', 'quantity']

admin.site.register(Flower, FlowerAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PlantRevivalTip, FlowerCareTipAdmin)
admin.site.register(CartItem, CartFlowerItem)