# Werchaback/orders/serializers.py
from rest_framework import serializers
from django.db import transaction
from catalog.models import Product
from .models import Order, OrderItem
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

    # ── ولیدیشن فیلدها برای پیام دقیق
    def validate_full_name(self, v):
        if len(v.strip()) < 3:
            raise serializers.ValidationError('نام و نام‌خانوادگی را کامل وارد کنید.')
        return v.strip()

    def validate_phone(self, v):
        s = v.strip()
        if not (re.fullmatch(r'09\d{9}', s) or re.fullmatch(r'\+989\d{9}', s)):
            raise serializers.ValidationError('شماره تماس معتبر نیست (نمونه: 09123456789).')
        return s

    def validate_postal_code(self, v):
        s = v.strip().replace('-', '').replace(' ', '')
        if not re.fullmatch(r'\d{10}', s):
            raise serializers.ValidationError('کد پستی باید ۱۰ رقم باشد.')
        return s

    def validate_city(self, v):
        if len(v.strip()) < 2:
            raise serializers.ValidationError('نام شهر معتبر نیست.')
        return v.strip()

    def validate_address(self, v):
        if len(v.strip()) < 10:
            raise serializers.ValidationError('آدرس باید حداقل ۱۰ کاراکتر باشد.')
        return v.strip()

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('سبد خرید خالی است.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        """
        استراتژی: اول همه آیتم‌ها را با lock بررسی می‌کنیم (بدون ایجاد سفارش).
        اگر هر خطایی بود، همون‌جا برمی‌گردیم (با available و title).
        اگر نبود، بعد Order + OrderItem می‌سازیم و stock کم می‌کنیم.
        """
        user = self.context['request'].user
        items_in = validated_data.pop('items')

        # قفل برای همزمانی
        ids = [i['product_id'] for i in items_in]
        products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=ids)}

        # مرحله‌ی 1: ولیدیشن آیتم‌ها
        errors = []
        computed = []  # (p, qty, unit_price, subtotal)
        total = 0

        for it in items_in:
            pid = it['product_id']
            qty = it['qty']
            p = products.get(pid)
            if not p:
                errors.append({'product_id': pid, 'detail': 'محصول یافت نشد'})
                continue

            unit = p.price
            # فقط به stock تکیه می‌کنیم (in_stock مشتق از stock است)
            if p.stock < qty:
                errors.append({
                    'product_id': p.id,
                    'title': p.title,
                    'available': p.stock,  # برای UX بهتر در فرانت
                    'detail': 'موجودی کافی نیست',
                })
                continue

            subtotal = unit * qty
            computed.append((p, qty, unit, subtotal))
            total += subtotal

        if errors:
            # هیچ تغییری انجام نشده؛ همان‌جا خطا بده
            raise serializers.ValidationError({'items': errors})

        # مرحله‌ی 2: ایجاد سفارش + آیتم‌ها + کسر موجودی
        order = Order.objects.create(user=user, **validated_data)
        for (p, qty, unit, subtotal) in computed:
            OrderItem.objects.create(
                order=order,
                product=p,
                title=p.title,          # snapshot
                unit_price=unit,
                qty=qty,
                subtotal=subtotal,
            )
            p.stock -= qty
            if p.stock <= 0:
                p.in_stock = False     # اگر save مدل شما sync می‌کند، این هم خودکار می‌شود
            p.save(update_fields=['stock', 'in_stock'])

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order


class OrderOutSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'created_at', 'items')

    def get_items(self, obj):
        return [{
            'product_id': it.product_id,
            'title': it.title,
            'qty': it.qty,
            'unit_price': it.unit_price,
            'subtotal': it.subtotal,
        } for it in obj.items.all()]


# ↓↓↓ خروجی مخصوص پرکردن خودکار آدرس
class LastAddressOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('full_name', 'phone', 'address', 'city', 'postal_code')