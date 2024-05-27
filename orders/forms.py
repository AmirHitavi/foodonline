from django import forms

from orders import models as orders_models


class OrderForm(forms.ModelForm):

    class Meta:
        model = orders_models.Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
        ]
