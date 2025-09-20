from django.db.models import Q, QuerySet
from .models import Post

def public_posts_qs() -> QuerySet:
    return Post.objects.filter(status=Post.PUBLISHED)

def apply_filters(qs: QuerySet, *, q: str | None, category: str | None, featured: str | None, ordering: str | None) -> QuerySet:
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content_html__icontains=q))
    if category:
        qs = qs.filter(category__slug=category)
    if featured in ("1", "true", "True"):
        qs = qs.filter(is_featured=True)

    # مرتب‌سازی
    allowed_order = {
        "new": "-published_at",
        "old": "published_at",
        "title": "title",
        "-title": "-title",
    }
    if ordering in allowed_order:
        qs = qs.order_by(allowed_order[ordering])
    else:
        qs = qs.order_by("-published_at", "-created_at")
    return qs
