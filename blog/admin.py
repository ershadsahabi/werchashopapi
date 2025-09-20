from django.contrib import admin
from .models import Category, Reference, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "year")
    search_fields = ("title", "source", "authors_text")
    list_filter = ("source", "year")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "published_at", "is_featured")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("title", "excerpt", "content_html", "seo_title", "meta_description")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category", "references", "author")
    date_hierarchy = "published_at"
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "excerpt", "content_html", "cover", "category", "references")}),
        ("SEO", {"fields": ("seo_title", "meta_description")}),
        ("Meta", {"fields": ("status", "is_featured", "reading_time_min", "published_at", "author")}),
    )
