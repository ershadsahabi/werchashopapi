from rest_framework import serializers
from django.db import transaction
from catalog.models import Product
from .models import Order, OrderItem


class OrderItemInSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInSerializer(many=True)
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('سبد خرید خالی است.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        items = validated_data.pop('items')

        # جمع‌آوری محصولات
        ids = [i['product_id'] for i in items]
        products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=ids)}

        order = Order.objects.create(user=user, **validated_data)

        total = 0
        errors = []
        for it in items:
            p = products.get(it['product_id'])
            if not p:
                errors.append({'product_id': it['product_id'], 'detail': 'محصول یافت نشد'})
                continue
            if not p.in_stock or p.stock < it['qty']:
                errors.append({'product_id': p.id, 'detail': 'موجودی کافی نیست'})
                continue

            unit = p.price
            qty = it['qty']
            subtotal = unit * qty

            OrderItem.objects.create(
                order=order,
                product=p,
                title=p.title,
                unit_price=unit,
                qty=qty,
                subtotal=subtotal,
            )
            # کسر موجودی ساده (در دنیای واقعی رزرو/پرداخت considerations)
            p.stock -= qty
            if p.stock <= 0:
                p.in_stock = False
            p.save(update_fields=['stock', 'in_stock'])

            total += subtotal

        if errors:
            # اگر هر خطایی بود، تراکنش را رول‌ بک کنیم
            raise serializers.ValidationError({'items': errors})

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order


class OrderOutSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'created_at', 'items')

    def get_items(self, obj):
        return [
            {
                'product_id': it.product_id,
                'title': it.title,
                'qty': it.qty,
                'unit_price': it.unit_price,
                'subtotal': it.subtotal,
            }
            for it in obj.items.all()
        ]