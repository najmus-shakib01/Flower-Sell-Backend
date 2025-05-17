from django.urls import path
from .views import IsAdminView

urlpatterns = [
    path('', IsAdminView.as_view(), name='is_admin'),
]