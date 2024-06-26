from django.contrib import admin

from .models import User, UserProfile

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ["password"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
