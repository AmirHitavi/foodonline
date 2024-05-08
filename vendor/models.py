from django.db import models

from accounts import models as accounts_models

# Create your models here.


class Vendor(models.Model):
    user = models.OneToOneField(
        accounts_models.User, related_name="user", on_delete=models.CASCADE
    )
    user_profile = models.OneToOneField(
        accounts_models.UserProfile,
        related_name="user_profile",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
