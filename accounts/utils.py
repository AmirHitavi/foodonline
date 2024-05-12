from django.core.exceptions import PermissionDenied


def detect_user(user):
    redirect_url = ""
    if user.role == 1:
        redirect_url = "vendor-dashboard"
    elif user.role == 2:
        redirect_url = "customer-dashboard"
    elif user.role is None and user.is_superuser:
        redirect_url = "/admin"

    return redirect_url


def check_role_vendor(user):
    """
    Restrict the vendor from accessing the customer page
    """

    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    """
    Restrict the customer from accessing the vendor page
    """

    if user.role == 2:
        return True
    else:
        raise PermissionDenied
