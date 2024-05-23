from django.contrib import admin

from .models import Category, FoodItem

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "vendor", "modified_at"]
    search_fields = ["name", "vendor__name"]


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("food_title",)}
    list_display = [
        "food_title",
        "category",
        "vendor",
        "price",
        "is_available",
        "modified_at",
    ]
    search_fields = ["food_title", "category__name", "vendor__name", "price"]
    list_filter = ["is_available"]
    list_editable = ["is_available"]
