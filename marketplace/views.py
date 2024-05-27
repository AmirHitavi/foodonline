from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts import models as accounts_models
from marketplace import context_processors as market_context_processors
from marketplace import models as market_models
from menu import models as menu_models
from orders import forms as orders_forms
from orders import models as orders_models
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

    opening_hours = vendor_models.OpeningHour.objects.filter(vendor=vendor).order_by(
        "day", "-from_hour"
    )

    today = datetime.today().isoweekday()
    current_opening_hours = vendor_models.OpeningHour.objects.filter(
        vendor=vendor, day=today
    ).order_by("day", "-from_hour")

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

    context = {
        "vendor": vendor,
        "opening_hours": opening_hours,
        "current_opening_hours": current_opening_hours,
        "categories": categories,
        "cart_items": cart_items,
    }
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


def search(request):
    if (
        not "address" in request.GET
        or not "keyword" in request.GET
        or not "lat" in request.GET
        or not "long" in request.GET
        or not "radius" in request.GET
    ):
        return redirect("marketplace")
    else:
        keyword = request.GET.get("keyword")
        address = request.GET.get("address")
        latitude = request.GET.get("lat")
        longitude = request.GET.get("long")
        radius = request.GET.get("radius")

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_food_items = menu_models.FoodItem.objects.filter(
            food_title__icontains=keyword, is_available=True
        ).values_list("vendor", flat=True)

        vendors = vendor_models.Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_food_items)
            | Q(name__icontains=keyword, user__is_active=True, is_approved=True)
        )

        if latitude and longitude and radius:
            point = GEOSGeometry(f"POINT({longitude} {latitude})", srid=4326)

            vendors = (
                vendor_models.Vendor.objects.filter(
                    Q(id__in=fetch_vendors_by_food_items)
                    | Q(
                        name__icontains=keyword, is_approved=True, user__is_active=True
                    ),
                    user_profile__location__distance__lte=(point, D(km=radius)),
                )
                .annotate(distance=Distance("user_profile__location", point))
                .order_by("distance")
            )

            for vendor in vendors:
                vendor.kms = round(vendor.distance.km, 1)
        context = {
            "vendors": vendors,
            "vendors_count": vendors.count(),
            "source_location": address,
        }

        return render(request, "marketplace/marketplace.html", context)


@login_required(login_url="login")
def checkout(request):
    cart_items = market_models.Cart.objects.filter(user=request.user).order_by(
        "created_at"
    )
    if cart_items.count() <= 0:
        return redirect("marketplace")

    user_profile = accounts_models.UserProfile.objects.get(user=request.user)

    default_values = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone": request.user.phone,
        "email": request.user.email,
        "address": user_profile.address,
        "country": user_profile.country,
        "state": user_profile.state,
        "city": user_profile.city,
        "pin_code": user_profile.pin_code,
    }

    form = orders_forms.OrderForm(initial=default_values)
    print("errors", form.errors)

    context = {"form": form, "cart_items": cart_items}
    return render(request, "marketplace/checkout.html", context)
