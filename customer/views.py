import simplejson as json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from accounts.utils import check_role_customer
from orders import models as orders_models

# Create your views here.


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_profile(request):
    user_profile = accounts_models.UserProfile.objects.get(user=request.user)
    user_form = accounts_forms.UserCustomerForm(instance=request.user)
    user_profile_form = accounts_forms.UserProfileForm(instance=user_profile)

    if request.method == "POST":
        user_form = accounts_forms.UserCustomerForm(request.POST, instance=request.user)
        user_profile_form = accounts_forms.UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        if user_form.is_valid() and user_profile_form.is_valid():
            user_profile.save()
            user_profile_form.save()
            messages.success(request, "Setting Updated")
            return redirect("customer-profile")
    context = {
        "user_profile": user_profile,
        "user_form": user_form,
        "user_profile_form": user_profile_form,
    }
    return render(request, "customer/customer_profile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def my_orders(request):
    orders = orders_models.Order.objects.filter(
        user=request.user, is_ordered=True
    ).order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "customer/my_orders.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def order_details(request, order_number):
    try:
        order = orders_models.Order.objects.get(
            order_number=order_number, is_ordered=True
        )
        ordered_foods = orders_models.OrderedFood.objects.filter(order=order)

        sub_total = 0
        for food in ordered_foods:
            sub_total += food.price * food.quantity

        tax_data = json.loads(order.tax_data)

        context = {
            "order": order,
            "ordered_foods": ordered_foods,
            "sub_total": sub_total,
            "tax_data": tax_data,
        }

        return render(request, "customer/order_details.html", context)

    except orders_models.Order.DoesNotExist:
        return redirect("customer")
