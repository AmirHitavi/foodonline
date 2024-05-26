from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from accounts.utils import check_role_vendor
from menu import forms as menu_forms
from menu import models as menu_models
from vendor import forms as vendor_forms
from vendor import models as vendor_models

# Create your views here.


def get_vendor(request):
    return vendor_models.Vendor.objects.get(user=request.user)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_profile(request):
    user_profile = get_object_or_404(accounts_models.UserProfile, user=request.user)
    vendor = get_object_or_404(vendor_models.Vendor, user=request.user)

    if request.method == "POST":
        user_profile_form = accounts_forms.UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        vendor_form = vendor_forms.VendorForm(
            request.POST, request.FILES, instance=vendor
        )
        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()

            messages.success(request, "Setting updated.")
            return redirect("vendor-profile")
    else:
        user_profile_form = accounts_forms.UserProfileForm(instance=user_profile)
        vendor_form = vendor_forms.VendorForm(instance=vendor)

    context = {
        "user_profile": user_profile,
        "user_profile_form": user_profile_form,
        "vendor": vendor,
        "vendor_form": vendor_form,
    }

    return render(request, "vendor/vendor_profile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = menu_models.Category.objects.filter(vendor=vendor)

    context = {
        "vendor": vendor,
        "categories": categories,
    }
    return render(request, "vendor/menu_builder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menu_builder_category(request, slug):
    vendor = get_vendor(request)
    category = get_object_or_404(menu_models.Category, slug=slug)
    food_items = menu_models.FoodItem.objects.filter(vendor=vendor, category=category)

    context = {"vendor": vendor, "category": category, "food_items": food_items}

    return render(request, "vendor/menu_builder_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_category(request):
    vendor = get_vendor(request)
    form = menu_forms.CategoryForm()

    if request.method == "POST":
        form = menu_forms.CategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = f"{slugify(name)}-{category.id}"
            category.save()

            messages.success(request, "Category added successfully!")
            return redirect("menu-builder")

    context = {"form": form}

    return render(request, "vendor/add_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_category(request, slug):
    category = get_object_or_404(menu_models.Category, slug=slug)
    form = menu_forms.CategoryForm(instance=category)

    if request.method == "POST":
        form = menu_forms.CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category.name)
            category.save()

            messages.info(request, "Category edited successfully!")
            return redirect("menu-builder")

    context = {"category": category, "form": form}

    return render(request, "vendor/edit_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_category(request, slug):
    category = get_object_or_404(menu_models.Category, slug=slug)
    category.delete()
    messages.error(request, "Category deleted successfully!")
    return redirect("menu-builder")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_food(request):
    form = menu_forms.FoodItemForm()
    form.fields["category"].queryset = menu_models.Category.objects.filter(
        vendor=get_vendor(request)
    )

    if request.method == "POST":
        form = menu_forms.FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data["food_title"]

            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            food_item.save()

            messages.success(request, "Food added successfully!")
            return redirect("menu-builder-category", food_item.category.slug)
        else:
            print(form.errors)

    context = {"form": form}
    return render(request, "vendor/add_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_food(request, slug):
    food_item = get_object_or_404(menu_models.FoodItem, slug=slug)
    form = menu_forms.FoodItemForm(instance=food_item)
    form.fields["category"].queryset = menu_models.Category.objects.filter(
        vendor=get_vendor(request)
    )

    if request.method == "POST":
        form = menu_forms.FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            food_title = form.cleaned_data["food_title"]

            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            food_item.save()

            messages.info(request, "Food Item edited successfully!")
            return redirect("menu-builder-category", food_item.category.slug)

    context = {"food_item": food_item, "form": form}

    return render(request, "vendor/edit_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_food(request, slug):
    food_item = get_object_or_404(
        menu_models.FoodItem, slug=slug, vendor=get_vendor(request)
    )
    category = food_item.category
    food_item.delete()
    messages.error(request, "Food Item deleted successfully!")
    return redirect("menu-builder-category", category.slug)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def opening_hour(request):
    form = vendor_forms.OpeningHoursForm()
    vendor = get_vendor(request)
    opening_hours = vendor_models.OpeningHour.objects.filter(vendor=vendor)

    context = {"form": form, "opening_hours": opening_hours}

    return render(request, "vendor/opening_hour.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_opening_hour(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        day = request.POST.get("day")
        from_hour = request.POST.get("from_hour")
        to_hour = request.POST.get("to_hour")
        is_closed = request.POST.get("is_closed")

        try:
            hour = vendor_models.OpeningHour.objects.create(
                vendor=get_vendor(request),
                day=day,
                from_hour=from_hour,
                to_hour=to_hour,
                is_closed=is_closed,
            )

            if hour:
                day = vendor_models.OpeningHour.objects.get(id=hour.id)

                if day.is_closed:
                    response = {
                        "status": "success",
                        "id": day.id,
                        "day": day.get_day_display(),
                        "is_closed": "Closed",
                    }
                else:
                    response = {
                        "status": "success",
                        "id": day.id,
                        "day": day.get_day_display(),
                        "from_hour": day.from_hour,
                        "to_hour": day.to_hour,
                    }

                return JsonResponse(response)

        except IntegrityError:
            return JsonResponse(
                {
                    "status": "failed",
                    "message": f"{from_hour}-{to_hour} already exists for this day!",
                }
            )
    else:
        return JsonResponse({"status": "failed", "message": "Invalid request!"})


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_opening_hour(request, id):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        try:
            hour = vendor_models.OpeningHour.objects.get(id=id)
            hour.delete()
            return JsonResponse({"status": "success", "id": id})
        except vendor_models.OpeningHour.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Opening hour not found"}
            )
    else:
        return JsonResponse({"status": "failed", "message": "Invalid request!"})
