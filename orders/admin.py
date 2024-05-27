from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    pass
