from rest_framework import serializers
from .models import Post, Category, Reference

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ["id", "title", "url", "authors_text", "year", "source", "abstract", "notes"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]

class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "excerpt", "cover",
            "category", "reading_time_min", "published_at", "is_featured",
            "seo_title", "meta_description"
        ]

class PostDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "excerpt", "content_html", "cover",
            "category", "reading_time_min", "published_at", "is_featured",
            "seo_title", "meta_description", "references"
        ]
