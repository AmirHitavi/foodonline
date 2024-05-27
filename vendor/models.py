from datetime import date, datetime, time

from django.db import models

from accounts import models as accounts_models
from accounts.utils import send_notification_email

# Create your models here.

DAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]

HOURS_OF_DAY = [
    (
        time(hour=h, minute=m).strftime("%I:%M %p"),
        time(hour=h, minute=m).strftime("%I:%M %p"),
    )
    for h in range(0, 24)
    for m in [0, 30]
]


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

    def clean(self):
        self.name = self.name.capitalize()

    def is_open(self):
        today = date.today().isoweekday()
        now = datetime.now().strftime("%I:%M %p")
        current_hours = OpeningHour.objects.filter(vendor=self, day=today)

        is_open = None
        for current_hour in current_hours:
            if not current_hour.is_closed:
                start = current_hour.from_hour
                end = current_hour.to_hour
                if start <= now <= end:
                    is_open = True
                    break
        else:
            is_open = False
        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original_object = Vendor.objects.get(pk=self.pk)
            if original_object.is_approved != self.is_approved:
                email_template = "emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                    "to_email": self.user.email,
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


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(max_length=25, choices=HOURS_OF_DAY, blank=True)
    to_hour = models.CharField(max_length=25, choices=HOURS_OF_DAY, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self):
        return self.get_day_display()
