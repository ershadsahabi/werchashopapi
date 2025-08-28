from django.contrib import admin
from .models import Category, Brand, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('key', 'label')
    search_fields = ('key', 'label')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category', 'brand', 'in_stock', 'stock', 'badge', 'rating')
    list_filter = ('category', 'brand', 'in_stock', 'badge')
    search_fields = ('title', 'slug', 'brand__name')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]