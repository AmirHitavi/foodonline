from django.db import models

from accounts import models as accounts_models
from menu import models as menu_models

# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(accounts_models.User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(menu_models.FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user
