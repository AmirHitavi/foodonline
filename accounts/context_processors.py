from django.conf import settings

from accounts import models as accounts_models

def get_google_api(request):
    return dict(GOOGLE_API_KEY=settings.GOOGLE_API)


def get_geo_api(request):
    return dict(GEO_API_KEY=settings.GEO_API_KEY)


def get_user_profile(request):
    try:
        user_profile = accounts_models.UserProfile.objects.get(user=request.user)
    except accounts_models.UserProfile.DoesNotExist:
        user_profile = None

    return dict(user_profile=user_profile)