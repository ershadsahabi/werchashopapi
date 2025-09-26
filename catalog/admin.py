# Werch_app/Werchaback/catalog/admin.py
from django.contrib import admin
from django.urls import reverse
from django.db.models import Count
from django.utils.html import format_html
from urllib.parse import urlencode

from .models import Category, Brand, Product, ProductImage


# ---------- Category ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # ستون‌ها
    list_display = (
        "thumb",        # پیش‌نمایش تصویر
        "label",
        "key",
        "is_active",
        "sort_order",
        "products_count_link",  # تعداد محصولات (با لینک به لیست محصولات فیلتر‌شده)
    )
    list_display_links = ("label", "key")
    list_editable = ("is_active", "sort_order")
    search_fields = ("label", "key", "description")
    list_filter = ("is_active",)
    ordering = ("sort_order", "label")
    prepopulated_fields = {"key": ("label",)}  # تولید خودکار key از label

    # چیدمان فرم
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("label", "key", "description", "is_active", "sort_order")
        }),
        ("تصویر", {
            "fields": ("image", "image_preview"),
        }),
    )
    readonly_fields = ("image_preview",)

    # برای شمارش سریع محصولات، annotate می‌کنیم
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_products_count=Count("products"))

    # پیش‌نمایش کوچک در لیست
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.image.url)
        return "—"
    thumb.short_description = "تصویر"

    # پیش‌نمایش بزرگ‌تر داخل فرم
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:160px;border-radius:8px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "پیش‌نمایش"

    # تعداد محصولات + لینک به لیست محصولات همین دسته
    def products_count_link(self, obj):
        count = getattr(obj, "_products_count", 0)
        url = (
            reverse("admin:catalog_product_changelist")
            + "?"
            + urlencode({"category__id__exact": obj.id})
        )
        return format_html('<a href="{}">{}</a>', url, count)
    products_count_link.short_description = "تعداد محصولات"

    # اکشن‌های گروهی فعال/غیرفعال
    actions = ["make_active", "make_inactive"]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} دسته‌بندی فعال شد.")
    make_active.short_description = "فعال‌کردن دسته‌بندی‌های انتخاب‌شده"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} دسته‌بندی غیرفعال شد.")
    make_inactive.short_description = "غیرفعال‌کردن دسته‌بندی‌های انتخاب‌شده"


# ---------- Brand ----------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


# ---------- ProductImage Inline ----------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ---------- Product ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "category", "brand", "in_stock", "stock", "badge", "rating")
    list_filter = ("category", "brand", "in_stock", "badge")
    search_fields = ("title", "slug", "brand__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
    autocomplete_fields = ("category", "brand")  # بهتر برای دیتاست‌های بزرگ
