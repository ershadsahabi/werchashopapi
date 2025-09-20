from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.utils import timezone

from .models import Post, Category, Reference
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    CategorySerializer, ReferenceSerializer
)
from .permissions import ReadOnlyOrStaff
from .pagination import DefaultPagination
from .selectors import public_posts_qs, apply_filters

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = "slug"
    throttle_scope = 'public_read'      


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all().order_by("title")
    serializer_class = ReferenceSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    لیست/جزئیات پست‌های منتشرشده برای همه آزاد است.
    پیش‌فرض پروژه IsAuthenticated است، پس اینجا AllowAny گذاشتیم.
    """
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    lookup_field = "slug"
    throttle_scope = 'public_read'      


    def get_queryset(self):
        qs = public_posts_qs().filter(published_at__lte=timezone.now())
        q = self.request.query_params.get("q")
        category = self.request.query_params.get("category")
        featured = self.request.query_params.get("featured")
        ordering = self.request.query_params.get("ordering")  # new|old|title|-title
        qs = apply_filters(qs, q=q, category=category, featured=featured, ordering=ordering)
        return qs.select_related("category", "author").prefetch_related("references")

    def get_serializer_class(self):
        if self.action in ("retrieve", ):
            return PostDetailSerializer
        return PostListSerializer

    @action(detail=False, permission_classes=[AllowAny], pagination_class=None)
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:6]
        ser = PostListSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)
