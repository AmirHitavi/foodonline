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
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = market_models.Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            sub_total += cart_item.food_item.price * cart_item.quantity

        grand_total = sub_total + tax

    return dict(sub_total=sub_total, tax=tax, grand_total=grand_total)
