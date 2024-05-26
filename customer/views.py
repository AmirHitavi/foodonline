from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.utils import check_role_customer
from accounts import models as accounts_models
from accounts import forms as accounts_forms

# Create your views here.


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_profile(request):
    user_profile = accounts_models.UserProfile.objects.get(user=request.user)
    user_form = accounts_forms.UserCustomerForm(instance=request.user)
    user_profile_form = accounts_forms.UserProfileForm(instance=user_profile)

    if request.method == "POST":
        user_form = accounts_forms.UserCustomerForm(request.POST, instance=request.user)
        user_profile_form = accounts_forms.UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_profile.save()
            user_profile_form.save()
            messages.success(request, "Setting Updated")
            return redirect('customer-profile')
    context = {
        'user_profile': user_profile,
        'user_form': user_form,
        'user_profile_form': user_profile_form
    }
    return render(request, "customer/customer_profile.html", context)
