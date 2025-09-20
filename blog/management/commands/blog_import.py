import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from blog.models import Category, Reference, Post
from django.db import transaction

class Command(BaseCommand):
    help = "Import blog data (idempotent) from a simple JSON (categories/references/posts). Upsert by slug/url."

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Path to JSON file")

        parser.add_argument("--dry-run", action="store_true", help="Validate only, no DB writes")

    def handle(self, *args, **opts):
        p = Path(opts["json_path"])
        if not p.exists():
            raise CommandError("JSON file not found")

        data = json.loads(p.read_text(encoding="utf-8"))
        cats = data.get("categories", [])
        refs = data.get("references", [])
        posts = data.get("posts", [])

        created, updated = {"cat":0,"ref":0,"post":0}, {"cat":0,"ref":0,"post":0}

        self.stdout.write(self.style.NOTICE(f"Importing: {len(cats)} categories, {len(refs)} references, {len(posts)} posts"))

        @transaction.atomic
        def do_import():
            # Categories
            cat_map = {}
            for c in cats:
                slug = c["slug"].strip()
                obj, was_created = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": c.get("name", slug),
                        "description": c.get("description", ""),
                    },
                )
                cat_map[slug] = obj
                (created if was_created else updated)["cat"] += 1

            # References (upsert by URL)
            ref_map = {}
            for r in refs:
                url = r["url"].strip()
                defaults = {
                    "title": r.get("title", url),
                    "authors_text": r.get("authors_text", ""),
                    "year": r.get("year", ""),
                    "source": r.get("source", ""),
                    "abstract": r.get("abstract", ""),
                    "notes": r.get("notes", ""),
                }
                obj, was_created = Reference.objects.update_or_create(url=url, defaults=defaults)
                ref_map[url] = obj
                (created if was_created else updated)["ref"] += 1

            # Posts (upsert by slug)
            for p in posts:
                slug = p["slug"].strip()
                defaults = {
                    "title": p.get("title", slug),
                    "excerpt": p.get("excerpt", ""),
                    "content_html": p.get("content_html", ""),
                    "cover": p.get("cover", None),
                    "reading_time_min": p.get("reading_time_min", 0),
                    "is_featured": bool(p.get("is_featured", False)),
                    "seo_title": p.get("seo_title",""),
                    "meta_description": p.get("meta_description",""),
                }
                # status/published_at اختیاری: اگر published_at هست → published
                published_at = p.get("published_at")
                if published_at:
                    defaults["status"] = Post.PUBLISHED
                    defaults["published_at"] = published_at
                else:
                    defaults["status"] = Post.DRAFT

                # دسته
                cat_slug = p.get("category_slug")
                if cat_slug:
                    defaults["category"] = cat_map.get(cat_slug)

                obj, was_created = Post.objects.update_or_create(slug=slug, defaults=defaults)
                (created if was_created else updated)["post"] += 1

                # روابط مرجع
                refs_urls = p.get("references_urls", [])
                if refs_urls:
                    obj.references.set([ref_map[u] for u in refs_urls if u in ref_map])
                else:
                    obj.references.clear()

        if opts["dry_run"]:
            self.stdout.write(self.style.WARNING("DRY-RUN: validating…"))
            try:
                with transaction.atomic():
                    do_import()
                    raise RuntimeError("Rollback dry-run")
            except RuntimeError:
                pass
        else:
            do_import()

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {created}  Updated: {updated}"
        ))
