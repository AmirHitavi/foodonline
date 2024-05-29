import json

from django.db import models

from accounts import models as accounts_models
from menu import models as menu_models
from vendor import models as vendor_models

request_object = ""


class Payment(models.Model):
    PAYMENT_METHOD = (("PayPal", "PayPal"),)
    user = models.ForeignKey(accounts_models.User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    user = models.ForeignKey(accounts_models.User, on_delete=models.CASCADE, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True
    )
    vendors = models.ManyToManyField(vendor_models.Vendor, blank=True)

    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=50)
    total = models.FloatField()
    tax_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Data format: {'tax_type': {'tax_percentage': 'tax_amount'}}",
    )
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=25, choices=STATUS, default="New")
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def order_placed_to(self):
        return ",".join([str(vendor) for vendor in self.vendors.all()])

    def get_total_by_vendor(self):
        sub_total = 0
        tax = 0
        tax_dict = {}
        grand_total = 0

        vendor = vendor_models.Vendor.objects.get(user=request_object.user)
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))

            for key, value in data.items():
                sub_total += float(key)
                if isinstance(value, str):  # Ensure value is a string before replacing
                    value = value.replace("'", '"')
                    value = json.loads(value)

                tax_dict.update(value)

                for tax_type, tax_values in value.items():
                    for percentage, amount in tax_values.items():
                        tax += float(amount)

        grand_total = float(tax) + float(sub_total)

        context = {
            "sub_total": sub_total,
            "tax_dict": tax_dict,
            "grand_total": grand_total,
        }
        return context

    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(accounts_models.User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(menu_models.FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_item.food_title
