from django.urls import path
from .views import (
    FlowerListAPIView, FlowerDetailAPIView, FlowerCareTipAPIView, CommentAPIView, 
    CommentShowAPIView, CommentCheckOrderAPIView, ContactFormView, 
    CommentEditAPIView, CartApiView
)

# URL Patterns
urlpatterns = [
    # Flower APIs
    path('flower_all/', FlowerListAPIView.as_view(), name='flower-list'),
    path('flower_detail/<int:pk>/', FlowerDetailAPIView.as_view(), name='flower-detail'),

    # Comment APIs
    path('comment_all/', CommentAPIView.as_view(), name='comments-api'),
    path('comment_delete/<int:commentId>/', CommentAPIView.as_view(), name='comment-delete'),
    path('comment_show/<int:flowerId>/', CommentShowAPIView.as_view(), name='get-comment'),
    path('comment_edit/<int:commentId>/', CommentEditAPIView.as_view(), name='comment-edit'),
    path('comment_check_order/', CommentCheckOrderAPIView.as_view(), name='check-order'),

    # Contact Form
    path('contact/', ContactFormView.as_view(), name='contact-form'),

    # Flower Care Tips
    path('care_tips/', FlowerCareTipAPIView.as_view(), name='flower-care-tips'),

    # Cart APIs
    path('cart/', CartApiView.as_view(), name='cart'),
    path('cart_remove/<int:cart_id>/', CartApiView.as_view(), name='cart-remove'),
]