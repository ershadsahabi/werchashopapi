import json
from pathlib import Path
from django.core.management.base import BaseCommand
from blog.models import Category, Reference, Post

class Command(BaseCommand):
    help = "Export blog data into a simple JSON (categories/references/posts) using natural keys (slug/url)."

    def add_arguments(self, parser):
        parser.add_argument("out_path", type=str, help="Output JSON path")
        parser.add_argument("--published-only", action="store_true", help="Export only published posts")
        parser.add_argument("--indent", type=int, default=2)

    def handle(self, *args, **opts):
        out = Path(opts["out_path"])
        qs_post = Post.objects.all().select_related("category").prefetch_related("references")
        if opts["published-only"]:
            qs_post = qs_post.filter(status=Post.PUBLISHED)

        data = {
            "categories": [
                {"slug": c.slug, "name": c.name, "description": c.description or ""}
                for c in Category.objects.all().order_by("name")
            ],
            "references": [
                {
                    "url": r.url,
                    "title": r.title,
                    "authors_text": r.authors_text,
                    "year": r.year,
                    "source": r.source,
                    "abstract": r.abstract,
                    "notes": r.notes,
                }
                for r in Reference.objects.all().order_by("title")
            ],
            "posts": []
        }

        for p in qs_post.order_by("-published_at","-created_at"):
            data["posts"].append({
                "slug": p.slug,
                "title": p.title,
                "excerpt": p.excerpt or "",
                "content_html": p.content_html or "",
                "cover": p.cover.name if p.cover else None,
                "category_slug": (p.category.slug if p.category else None),
                "reading_time_min": p.reading_time_min,
                "is_featured": p.is_featured,
                "published_at": (p.published_at.isoformat() if p.published_at else None),
                "references_urls": [r.url for r in p.references.all().order_by("title")],
                "seo_title": p.seo_title or "",
                "meta_description": p.meta_description or "",
            })

        out.write_text(json.dumps(data, ensure_ascii=False, indent=opts["indent"]), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote {out}"))
