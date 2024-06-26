"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import index
from marketplace.views import cart, checkout, search

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("cart/", cart, name="cart"),
    path("search/", search, name="search"),
    path("checkout/", checkout, name="checkout"),
    path("accounts/", include("accounts.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("orders/", include("orders.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
