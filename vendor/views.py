from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.utils import check_role_vendor
from accounts import forms as accounts_forms
from accounts import models as accounts_models
from vendor import forms as vendor_forms
from vendor import models as vendor_models

# Create your views here.


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_profile(request):
    user_profile = get_object_or_404(accounts_models.UserProfile, user=request.user)
    vendor = get_object_or_404(vendor_models.Vendor, user=request.user)

    if request.method == 'POST':
        user_profile_form = accounts_forms.UserProfileForm(request.POST, request.FILES, instance=user_profile)
        vendor_form = vendor_forms.VendorForm(request.POST, request.FILES, instance=vendor)
        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()

            messages.success(request, 'Setting updated.')
            return redirect('vendor-profile')
    else:
        user_profile_form = accounts_forms.UserProfileForm(instance=user_profile)
        vendor_form = vendor_forms.VendorForm(instance=vendor)

    context = {
        'user_profile': user_profile,
        'user_profile_form': user_profile_form,
        'vendor': vendor,
        'vendor_form': vendor_form
    }

    return render(request, "vendor/vendor_profile.html", context)
