from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from vendor import forms as vendor_forms

# Create your views here.
# TODO: User Registration and Vendor Registration
# TODO: Create view/url for registration of users and vendors and login and logout.


def index(request):
    return render(request, "accounts/index.html")


def register_user(request):
    form = accounts_forms.RegisterUserForm()

    if request.method == "POST":
        form = accounts_forms.RegisterUserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.set_password(password)
            user.role = accounts_models.User.CUSTOMER
            user.save()

            messages.success(request, "Your account has been created successfully!")
            return redirect("index")

    context = {"form": form}

    return render(request, "accounts/register_user.html", context)


def register_vendor(request):
    user_form = accounts_forms.RegisterUserForm()
    vendor_form = vendor_forms.VendorRegisterForm()

    if request.method == "POST":
        user_form = accounts_forms.RegisterUserForm(request.POST)
        vendor_form = vendor_forms.VendorRegisterForm(request.POST, request.FILES)
        if user_form.is_valid() and vendor_form.is_valid():
            # save the user instance
            user_password = user_form.cleaned_data["password"]
            user = user_form.save(commit=False)
            user.set_password(user_password)
            user.role = accounts_models.User.VENDOR
            user.save()

            # save the vendor instance
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = accounts_models.UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.slug = f"{slugify(vendor.name)}-{str(user.pk)}"
            vendor.save()

        messages.success(
            request,
            "Your account has been registered successfully!\nPlease wait for the approval.",
        )

        return redirect("index")

    context = {"user_form": user_form, "vendor_form": vendor_form}
    return render(request, "accounts/register_vendor.html", context)
