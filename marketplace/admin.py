from django.contrib import admin

from .models import Cart, Tax

# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ["tax_type", "tax_percentage", "is_active",]

