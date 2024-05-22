from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode

from accounts import forms as accounts_forms
from accounts import models as accounts_models
from vendor import forms as vendor_forms

from .utils import (
    check_role_customer,
    check_role_vendor,
    detect_user,
    send_verification_email,
)


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

            # send verification email
            mail_subject = "Please activate your account"
            email_template = "emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Your account has been created successfully!")
            return redirect("login")

    context = {"form": form}

    return render(request, "accounts/register_user.html", context)


def register_vendor(request):
    user_form = accounts_forms.RegisterUserForm()
    vendor_form = vendor_forms.VendorForm()

    if request.user.is_authenticated:
        messages.warning(request, "You already signed up.")
        return redirect(my_account)

    if request.method == "POST":
        user_form = accounts_forms.RegisterUserForm(request.POST)
        vendor_form = vendor_forms.VendorForm(request.POST, request.FILES)
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

            # send verification email
            mail_subject = "Please activate your account"
            email_template = "emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

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


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = accounts_models.User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, accounts_models.User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Congratulations! Your account is activated.")
        return redirect("my-account")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("my-account")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if accounts_models.User.objects.filter(email=email).exists:
            user = accounts_models.User.objects.get(email__exact=email)

            mail_subject = "Reset Your Password"
            email_template = "emails/reset_password.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request, "Password reset link has been sent to your email address."
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist!")
            return redirect("forgot-password")
    return render(request, "accounts/forgot_password.html")


def forgot_password_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = accounts_models.User.objects.get(pk=uid)
    except (
        ValueError,
        TypeError,
        KeyError,
        OverflowError,
        accounts_models.User.DoesNotExist,
    ):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("reset-password")
    else:
        messages.error(request, "This link has been expired!")
        return redirect("my-account")


def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password and confirm_password and password == confirm_password:
            pk = request.session.get("uid")
            user = accounts_models.User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()

            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password does not match")
            return redirect("reset-password")

    return render(request, "accounts/reset_password.html")
