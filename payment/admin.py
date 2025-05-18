from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_id', 'amount', 'status', 'created_at']

admin.site.register(Payment, PaymentAdmin)