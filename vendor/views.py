from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_vendor
from vendor import models as vendor_models
# Create your views here.


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_profile(request):
    vendor = vendor_models.Vendor.objects.get(user=request.user)

    context = {
        'vendor': vendor
    }

    return render(request, 'vendor/vendor_profile.html', context)
