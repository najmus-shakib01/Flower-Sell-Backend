from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('users.urls')),
    path('api/v1/flower/', include('flowers.urls')),
    path('api/v1/order/', include('orders.urls')),
    path('api/v1/admins/', include('admins.urls')),
    path('api/v1/pass_change/', include('pass_change.urls')),
    path('api/v1/payment/', include('payment.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  