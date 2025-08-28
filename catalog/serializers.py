from rest_framework import serializers
from .models import Product, ProductImage


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.key')
    brand = serializers.CharField(source='brand.name')
    badge = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'image', 'rating', 'in_stock', 'badge', 'category', 'brand')

    def get_image(self, obj):
        req = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            return req.build_absolute_uri(url) if req else url
        return None

    def get_badge(self, obj):
        return obj.badge_label


class ProductDetailSerializer(ProductListSerializer):
    images = serializers.SerializerMethodField()
    description = serializers.CharField()
    slug = serializers.CharField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ('description', 'slug', 'images')

    def get_images(self, obj):
        req = self.context.get('request')
        out = []
        for im in obj.images.all():
            url = im.image.url
            out.append({
                'url': req.build_absolute_uri(url) if req else url,
                'alt': im.alt or '',
            })
        return out