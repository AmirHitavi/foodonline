from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from accounts.utils import check_role_vendor
from vendor import forms as vendor_forms
from vendor import models as vendor_models
from menu import models as menu_models
from menu import forms as menu_forms

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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = menu_models.Category.objects.filter(vendor=vendor)

    context = {
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, "vendor/menu_builder.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder_category(request, slug):
    vendor = get_vendor(request)
    category = get_object_or_404(menu_models.Category, slug=slug)
    food_items = menu_models.FoodItem.objects.filter(vendor=vendor, category=category)

    context = {
        'vendor': vendor,
        'category': category,
        'food_items': food_items
    }

    return render(request, "vendor/menu_builder_category.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    vendor = get_vendor(request)
    form = menu_forms.CategoryForm()

    if request.method == 'POST':
        form = menu_forms.CategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = f'{slugify(name)}-{category.pk}'
            category.save()

            messages.success(request, 'Category added successfully!')
            return redirect('menu-builder')

    context = {
        'form': form
    }

    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, slug):
    category = get_object_or_404(menu_models.Category, slug=slug)
    form = menu_forms.CategoryForm(instance=category)

    if request.method == 'POST':
        form = menu_forms.CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category.name)
            category.save()

            messages.success(request, 'Category edited successfully!')
            return redirect('menu-builder')

    context = {
        'category': category,
        'form': form
    }

    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, slug):
    category = get_object_or_404(menu_models.Category, slug=slug)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('menu-builder')
