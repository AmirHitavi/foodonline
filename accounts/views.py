from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from vendor import forms as vendor_forms

from .utils import check_role_customer, check_role_vendor, detect_user


def index(request):
    return render(request, "accounts/index.html")


def register_user(request):
    form = accounts_forms.RegisterUserForm()

    if request.user.is_authenticated:
        messages.warning(request, "You already signed up.")
        return redirect(my_account)

    if request.method == "POST":
        form = accounts_forms.RegisterUserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.set_password(password)
            user.role = accounts_models.User.CUSTOMER
            user.save()

            messages.success(request, "Your account has been created successfully!")
            return redirect("login")

    context = {"form": form}

    return render(request, "accounts/register_user.html", context)


def register_vendor(request):
    user_form = accounts_forms.RegisterUserForm()
    vendor_form = vendor_forms.VendorRegisterForm()

    if request.user.is_authenticated:
        messages.warning(request, "You already signed up.")
        return redirect(my_account)

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

        return redirect("login")

    context = {"user_form": user_form, "vendor_form": vendor_form}
    return render(request, "accounts/register_vendor.html", context)


def login_user(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in!")
        return redirect("my-account")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("my-account")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout_user(request):
    auth.logout(request)
    messages.info(request, "You are logged out")
    return redirect("login")


@login_required(login_url="login")
def my_account(request):
    user = request.user
    redirect_to = detect_user(user)
    return redirect(redirect_to)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, "accounts/customer_dashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, "accounts/vendor_dashboard.html")
