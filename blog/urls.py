from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CategoryViewSet, ReferenceViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="blog-post")
router.register("categories", CategoryViewSet, basename="blog-category")
router.register("references", ReferenceViewSet, basename="blog-reference")

urlpatterns = [
    path("", include(router.urls)),
]
