import uuid
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    # مثال: key = 'dog' | 'cat' | 'bird' | 'small'
    key = models.SlugField(max_length=50, unique=True, db_index=True)
    label = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.label


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    BADGE_CHOICES = (
        ('sale', 'حراج'),
        ('new', 'جدید'),
    )

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)

    # قیمت را برای ساده‌سازی به تومان (عدد صحیح) نگه می‌داریم
    price = models.PositiveIntegerField()

    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')

    in_stock = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0)
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, blank=True, null=True)

    image = models.ImageField(upload_to='products/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['price']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]

    def __str__(self):
        return self.title

    @property
    def badge_label(self):
        if not self.badge:
            return None
        return dict(self.BADGE_CHOICES).get(self.badge)


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image of {self.product_id}"