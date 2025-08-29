from rest_framework import serializers
from django.db import transaction
from catalog.models import Product
from .models import Order, OrderItem
from collections import Counter
import re


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

    # ↓↓↓ اعتبارسنجی دقیق‌تر فیلدها (پیام‌های قابل‌مصرف در UI)
    def validate_full_name(self, v):
        if len(v.strip()) < 3:
            raise serializers.ValidationError('نام و نام‌خانوادگی را کامل وارد کنید.')
        return v.strip()

    def validate_phone(self, v):
        s = v.strip()
        # 09XXXXXXXXX یا +989XXXXXXXXX
        if not (re.fullmatch(r'09\d{9}', s) or re.fullmatch(r'\+989\d{9}', s)):
            raise serializers.ValidationError('شماره تماس معتبر نیست (نمونه: 09123456789).')
        return s

    def validate_postal_code(self, v):
        s = v.strip().replace('-', '').replace(' ', '')
        if not re.fullmatch(r'\d{10}', s):
            raise serializers.ValidationError('کد پستی باید ۱۰ رقم باشد.')
        return s

    def validate_address(self, v):
        if len(v.strip()) < 10:
            raise serializers.ValidationError('آدرس باید حداقل ۱۰ کاراکتر باشد.')
        return v.strip()

    def validate_city(self, v):
        if len(v.strip()) < 2:
            raise serializers.ValidationError('نام شهر معتبر نیست.')
        return v.strip()

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('سبد خرید خالی است.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        items = validated_data.pop('items')


        # ادغام آیتم‌های تکراری بر اساس product_id
        merged = Counter()
        for it in items:
            merged[it['product_id']] += it['qty']
        items = [{'product_id': pid, 'qty': q} for pid, q in merged.items()]
        
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
    

# ↓↓↓ خروجی مخصوص پرکردن خودکار آدرس
class LastAddressOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('full_name', 'phone', 'address', 'city', 'postal_code')