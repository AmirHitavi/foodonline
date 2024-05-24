from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from marketplace import context_processors as market_context_processors
from marketplace import models as market_models
from menu import models as menu_models
from vendor import models as vendor_models

# Create your views here.


def marketplace(request):
    vendors = vendor_models.Vendor.objects.filter(
        user__is_active=True, is_approved=True
    )

    context = {"vendors": vendors, "vendors_count": vendors.count()}

    return render(request, "marketplace/marketplace.html", context=context)


def vendor_details(request, slug):
    vendor = get_object_or_404(vendor_models.Vendor, slug=slug)
    categories = menu_models.Category.objects.prefetch_related(
        Prefetch(
            "fooditem_set",
            queryset=menu_models.FoodItem.objects.filter(is_available=True),
        )
    ).filter(vendor=vendor)

    if request.user.is_authenticated:

        cart_items = market_models.Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {"vendor": vendor, "categories": categories, "cart_items": cart_items}
    return render(request, "marketplace/vendor_details.html", context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # check if the request sent by ajax
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # check if the food item exists
            try:
                food_item = menu_models.FoodItem.objects.get(id=food_id)
                try:
                    # if cart item already exists then increment the quantity
                    cart_item = market_models.Cart.objects.get(
                        user=request.user, food_item=food_item
                    )
                    cart_item.quantity += 1
                    cart_item.save()

                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Increased the cart quantity",
                            "cart_counter": market_context_processors.get_cart_counter(
                                request
                            ),
                            "cart_amounts": market_context_processors.get_cart_amounts(
                                request
                            ),
                            "qty": cart_item.quantity,
                        }
                    )

                except market_models.Cart.DoesNotExist:
                    # if cart item does not exist, create a new one for the user
                    cart_item = market_models.Cart.objects.create(
                        user=request.user, food_item=food_item, quantity=1
                    )
                    cart_item.save()

                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Added the food to the cart",
                            "cart_counter": market_context_processors.get_cart_counter(
                                request
                            ),
                            "cart_amounts": market_context_processors.get_cart_amounts(
                                request
                            ),
                            "qty": cart_item.quantity,
                        }
                    )
            except menu_models.FoodItem.DoesNotExist:
                return JsonResponse(
                    {"status": "failed", "message": "This Food Item does not exist"}
                )
        else:
            return JsonResponse({"status": "failed", "message": "Invalid request"})
    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


def decrease_from_cart(request, food_id):
    if request.user.is_authenticated:
        # check if the request sent by ajax
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # check if the food item exists
            try:
                food_item = menu_models.FoodItem.objects.get(id=food_id)
                try:
                    # check if the user has already added that food to the cart
                    cart_item = market_models.Cart.objects.get(
                        user=request.user, food_item=food_item
                    )

                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()

                        return JsonResponse(
                            {
                                "status": "success",
                                "message": "Decreased the cart quantity",
                                "cart_counter": market_context_processors.get_cart_counter(
                                    request
                                ),
                                "cart_amounts": market_context_processors.get_cart_amounts(
                                    request
                                ),
                                "qty": cart_item.quantity,
                            }
                        )
                    else:
                        cart_item.delete()
                        cart_item.quantity = 0

                        return JsonResponse(
                            {
                                "status": "success",
                                "message": "Deleted the cart item",
                                "cart_counter": market_context_processors.get_cart_counter(
                                    request
                                ),
                                "cart_amounts": market_context_processors.get_cart_amounts(
                                    request
                                ),
                                "qty": cart_item.quantity,
                            }
                        )

                except market_models.Cart.DoesNotExist:
                    return JsonResponse(
                        {
                            "status": "failed",
                            "message": "You do not have this item in your cart!",
                        }
                    )
            except menu_models.FoodItem.DoesNotExist:
                return JsonResponse(
                    {"status": "failed", "message": "This Food Item does not exist"}
                )
        else:
            return JsonResponse({"status": "failed", "message": "Invalid request"})
    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


@login_required(login_url="login")
def cart(request):
    cart_items = market_models.Cart.objects.filter(user=request.user)

    context = {"cart_items": cart_items}
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        # check if the request sent by ajax
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # check if the cart item exists
            try:
                cart_item = market_models.Cart.objects.get(
                    id=cart_id, user=request.user
                )
                if cart_item:
                    cart_item.delete()

                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Delete the cart item",
                            "cart_counter": market_context_processors.get_cart_counter(
                                request
                            ),
                            "cart_amounts": market_context_processors.get_cart_amounts(
                                request
                            ),
                        }
                    )
            except market_models.Cart.DoesNotExist:
                return JsonResponse(
                    {
                        "status": "failed",
                        "message": "You do not have this item in your cart!",
                    }
                )
        else:
            return JsonResponse({"status": "failed", "message": "Invalid request"})
    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )
