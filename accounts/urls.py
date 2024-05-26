from django.urls import include, path

from accounts import views

urlpatterns = [
    path("register-user/", views.register_user, name="register-user"),
    path("register-vendor/", views.register_vendor, name="register-vendor"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("my-account/", views.my_account, name="my-account"),
    path("customer-dashboard/", views.customer_dashboard, name="customer-dashboard"),
    path("vendor-dashboard/", views.vendor_dashboard, name="vendor-dashboard"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path(
        "forgot-password-validation/<uidb64>/<token>/",
        views.forgot_password_validation,
        name="forgot-password-validation",
    ),
    path("reset-password/", views.reset_password, name="reset-password"),
    path("vendor/", include("vendor.urls")),
    path("customer/", include("customer.urls"))
]
