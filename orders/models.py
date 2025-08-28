import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت/تایید'),
        ('paid', 'پرداخت‌شده'),
        ('canceled', 'لغو شده'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    total_amount = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    title = models.CharField(max_length=200)  # snapshot
    unit_price = models.PositiveIntegerField()
    qty = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} x {self.qty}"