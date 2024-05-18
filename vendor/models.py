from django.db import models

from accounts import models as accounts_models
from accounts.utils import send_notification_email

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

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original_object = Vendor.objects.get(pk=self.pk)
            if original_object.is_approved != self.is_approved:
                email_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved
                }
                if self.is_approved:
                    # send notification email
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification_email(mail_subject, email_template, context)
                else:
                    # send notification email
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our platform."
                    send_notification_email(mail_subject, email_template, context)
        return super(Vendor, self).save(*args, **kwargs)