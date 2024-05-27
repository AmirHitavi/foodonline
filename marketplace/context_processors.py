from marketplace import models as market_models
from menu import models as menu_models


def get_cart_counter(request):
    cart_counter = 0

    if request.user.is_authenticated:
        try:
            cart_items = market_models.Cart.objects.filter(user=request.user)
            for cart_item in cart_items:
                cart_counter += cart_item.quantity
        except market_models.Cart.DoesNotExist:
            cart_counter = 0
    else:
        cart_counter = 0

    return dict(cart_counter=cart_counter)


def get_cart_amounts(request):
    sub_total = 0
    tax_dict = {}
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = market_models.Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            sub_total += cart_item.food_item.price * cart_item.quantity

        taxes = market_models.Tax.objects.filter(is_active=True)
        for current_tax in taxes:
            tax_type = current_tax.tax_type
            tax_percentage = current_tax.tax_percentage
            tax_amount = round((sub_total * tax_percentage) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        for value_i in tax_dict.values():
            for value_j in value_i.values():
                tax += value_j
        grand_total = sub_total + tax

    return dict(
        sub_total=sub_total, tax_dict=tax_dict, tax=tax, grand_total=grand_total
    )
