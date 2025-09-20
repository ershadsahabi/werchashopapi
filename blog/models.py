from django.db import models
from django.utils.text import slugify
from django.conf import settings

# اگر Postgres داری و ArrayField می‌خوای:
# from django.contrib.postgres.fields import ArrayField

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)


class Reference(models.Model):
    title = models.CharField(max_length=300)
    url = models.URLField()
    authors_text = models.CharField(max_length=500, blank=True)  # ساده و سازگار با همه DBها
    # اگر Postgres: authors = ArrayField(models.CharField(max_length=120), default=list, blank=True)
    year = models.CharField(max_length=10, blank=True)
    source = models.CharField(max_length=200, blank=True)
    abstract = models.TextField(blank=True)  # خلاصه برای نمایش در مدال/tooltip
    notes = models.TextField(blank=True)     # توضیح خودت

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Post(models.Model):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (PUBLISHED, "Published")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.TextField(blank=True)
    content_html = models.TextField(help_text="Rendered HTML (یا متن خام؛ بعداً می‌توان Markdown را رندر کرد)")
    # اگر با Markdown کار می‌کنی یک فیلد content_md هم اضافه کن و هنگام save تبدیل کن
    cover = models.ImageField(upload_to="blog/", blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    # برای برچسب‌ها بعداً می‌توان taggit اضافه کرد

    seo_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT, db_index=True)
    is_featured = models.BooleanField(default=False)
    reading_time_min = models.PositiveIntegerField(default=0, help_text="Approx. reading time in minutes")

    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_posts")
    references = models.ManyToManyField(Reference, blank=True, related_name="posts")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        # اگر reading_time_min خالی است، حدودی بر اساس تعداد کلمات محاسبه کن
        if self.content_html and not self.reading_time_min:
            # خیلی ساده: هر 250 کلمه ~ 1 دقیقه
            words = len(self.content_html.split())
            self.reading_time_min = max(1, words // 250)
        return super().save(*args, **kwargs)
