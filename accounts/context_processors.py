from django.conf import settings


def get_google_api(request):
    return dict(GOOGLE_API_KEY=settings.GOOGLE_API)


def get_geo_api(request):
    return dict(GEO_API_KEY=settings.GEO_API_KEY)
