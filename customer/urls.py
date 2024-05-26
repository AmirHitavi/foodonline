from django.urls import path
from accounts.views import customer_dashboard
from customer import views

urlpatterns = [
    path('', customer_dashboard, name="customer"),
    path("profile/", views.customer_profile, name="customer-profile")
]