from django.core.management.base import BaseCommand, CommandError
from blog.models import Post, Category
from django.utils import timezone
import pathlib

class Command(BaseCommand):
    help = "Import markdown files in a folder as blog posts (very basic)."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to folder containing .md files")
        parser.add_argument("--category", type=str, default="", help="Category name")

    def handle(self, *args, **options):
        folder = pathlib.Path(options["folder"])
        if not folder.exists():
            raise CommandError("Folder does not exist")

        category = None
        cat_name = options["category"].strip()
        if cat_name:
            category, _ = Category.objects.get_or_create(name=cat_name)

        for f in folder.glob("*.md"):
            title = f.stem.replace("-", " ").title()
            content = f.read_text(encoding="utf-8")
            p, created = Post.objects.get_or_create(
                title=title,
                defaults=dict(
                    content_html=content,  # فرض: همین را HTML گذاشتیم؛ در عمل باید Markdown→HTML رندر شود
                    excerpt=content[:200],
                    status=Post.PUBLISHED,
                    category=category,
                    published_at=timezone.now(),
                )
            )
            self.stdout.write(self.style.SUCCESS(f"{'CREATED' if created else 'SKIPPED'}: {p.title}"))
