from django.contrib import admin

from .models import OpeningHour, Vendor

# Register your models here.


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    pass


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    pass
