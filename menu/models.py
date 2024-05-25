from django.db import models
from django.utils.text import slugify
from vendor import models as vendor_models

# Create your models here.


class Category(models.Model):

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ("vendor", "name")

    vendor = models.ForeignKey(vendor_models.Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.capitalize()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(f"{self.name} {self.vendor.name} {self.vendor.id}")
        return super(Category, self).save(*args, **kwargs)


class FoodItem(models.Model):

    vendor = models.ForeignKey(vendor_models.Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    food_title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="vendor/food_images")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("food_title", "category", "vendor")

    def __str__(self):
        return self.food_title

    def clean(self):
        self.food_title = self.food_title.capitalize()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = slugify(
                f"{self.food_title} {self.category.name} {self.vendor.name} {self.vendor.id}"
            )
        return super(FoodItem, self).save(*args, **kwargs)
