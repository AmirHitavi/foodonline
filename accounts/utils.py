from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


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


def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL

    context = {
        "user": user,
        "domain": get_current_site(request),
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
    }
    message = render_to_string(email_template, context)

    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()


def send_notification_email(mail_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)

    if isinstance(context["to_email"], list):
        to_email = context["to_email"]
    elif isinstance(context["to_email"], str):
        to_email = [context["to_email"]]
    else:
        to_email = []

    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()
