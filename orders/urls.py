from django.urls import path
from .views import OrderCreateView, LastAddressView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('last-address/', LastAddressView.as_view(), name='order-last-address'),  # ← جدید

]