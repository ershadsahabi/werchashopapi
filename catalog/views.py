# Werch_app\Werchaback\catalog\views.py

from math import ceil
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Product, Category, Brand
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer

class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'public_read'

    def get(self, request):
        qs = Category.objects.filter(is_active=True)
        ser = CategorySerializer(qs, many=True, context={'request': request})
        return Response({'items': ser.data})


class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'public_read'

    def get(self, request):
        qs = Product.objects.select_related('category', 'brand').all()

        # دریافت پارامترها
        q = request.query_params.get('q')
        cat = request.query_params.get('cat')
        brand = request.query_params.get('brand')
        min_price = request.query_params.get('min')
        max_price = request.query_params.get('max')
        sort = request.query_params.get('sort', 'latest')
        page = int(request.query_params.get('page', '1'))
        page_size = int(request.query_params.get('page_size', '12'))

        # نرمال‌سازی مقادیر مشکوک
        def _clean(v):
            return None if v in (None, '', 'undefined', 'null') else v

        q = _clean(q)
        cat = _clean(cat)
        cats = Category.objects.filter(is_active=True).order_by('sort_order', 'label')
        cat_ser = CategorySerializer(cats, many=True, context={'request': request})
        brand = _clean(brand)
        brands = list(Brand.objects.order_by('name').values_list('name', flat=True))
        min_price = _clean(min_price)
        max_price = _clean(max_price)
        
        cats = Category.objects.filter(is_active=True).order_by('sort_order', 'label')
        cat_ser = CategorySerializer(cats, many=True, context={'request': request})


        # تبدیل امن به عدد
        try:
            if min_price is not None:
                min_price = int(min_price)
        except ValueError:
            min_price = None

        try:
            if max_price is not None:
                max_price = int(max_price)
        except ValueError:
            max_price = None

        # اعمال فیلترها
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(brand__name__icontains=q))
        if cat:
            qs = qs.filter(category__key=cat)
        if brand:
            qs = qs.filter(brand__name=brand)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)

        # مرتب‌سازی
        if sort == 'price-asc':
            qs = qs.order_by('price')
        elif sort == 'price-desc':
            qs = qs.order_by('-price')
        elif sort == 'rating':
            qs = qs.order_by('-rating')
        else:  # latest
            qs = qs.order_by('-id')

        # صفحه‌بندی
        total = qs.count()
        pages = max(1, ceil(total / page_size))
        page = max(1, min(page, pages))
        start = (page - 1) * page_size
        items = qs[start:start + page_size]

        # سریالایزر
        ser = ProductListSerializer(items, many=True, context={'request': request})

        # فست‌ها (facets)
        categories = list(Category.objects.values('key', 'label'))
        brands = list(Brand.objects.order_by('name').values_list('name', flat=True))

        return Response({
            'items': ser.data,
            'total': total,
            'pages': pages,
            'page': page,
            'facets': {
                'categories': cat_ser.data,   # ← الان شامل image/description هم هست
                'brands': brands,
            }       
        })


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            p = Product.objects.select_related('category', 'brand').prefetch_related('images').get(slug=slug)
        except Product.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        ser = ProductDetailSerializer(p, context={'request': request})
        return Response(ser.data)