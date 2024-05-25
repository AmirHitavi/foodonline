from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from .validators import valid_image_extensions

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, username, email, password=None):
        """
        Create a new User instance based on the given
        first name, last name, username, email and password.
        """
        if not first_name:
            raise ValueError("User must have first name.")
        if not last_name:
            raise ValueError("User must have last name.")
        if not username:
            raise ValueError("User must have username.")
        if not email:
            raise ValueError("User must have email address.")

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        """
        Create a new Super User instance based on the given
        first name, last name, username, email and password.
        """
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )

        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICES = [(VENDOR, "VENDOR"), (CUSTOMER, "CUSTOMER")]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)

    # Date fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Boolean fields
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "username",
    ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_role(self):
        return "Vendor" if self.role == 1 else "Customer"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="users/profile_picture",
        blank=True,
        null=True,
        validators=[valid_image_extensions],
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photo",
        blank=True,
        null=True,
        validators=[valid_image_extensions],
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=25, blank=True, null=True)
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.longitude and self.latitude:
            self.location = Point(float(self.longitude), float(self.latitude))
        return super(UserProfile, self).save(*args, **kwargs)
