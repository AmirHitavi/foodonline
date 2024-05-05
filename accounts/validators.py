import os

from django.core.exceptions import ValidationError

VALID_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def valid_image_extensions(value):
    extension = os.path.splitext(value.name)[1]

    if not extension.lower() in VALID_EXTENSIONS:
        raise ValidationError("Unsupported file extension.")
