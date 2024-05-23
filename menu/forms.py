from django import forms

from accounts.validators import valid_image_extensions
from menu import models as menu_models


class CategoryForm(forms.ModelForm):

    class Meta:
        model = menu_models.Category
        fields = ["name", "description"]


class FoodItemForm(forms.ModelForm):

    image = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[valid_image_extensions],
    )

    class Meta:
        model = menu_models.FoodItem
        fields = [
            "food_title",
            "category",
            "description",
            "price",
            "is_available",
            "image",
        ]
