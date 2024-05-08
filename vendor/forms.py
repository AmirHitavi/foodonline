from django import forms

from accounts.validators import valid_image_extensions
from vendor import models as vendor_models


class VendorRegisterForm(forms.ModelForm):

    license = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[valid_image_extensions],
    )

    class Meta:
        model = vendor_models.Vendor
        fields = ["name", "license"]
