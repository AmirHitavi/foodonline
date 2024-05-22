from django.urls import path

from . import views
from accounts import views as accounts_views


urlpatterns = [
    path("", accounts_views.vendor_dashboard, name="vendor"),
    path("profile/", views.vendor_profile, name="vendor-profile"),
]
