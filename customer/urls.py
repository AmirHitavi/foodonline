from django.urls import path

from accounts.views import customer_dashboard
from customer import views

urlpatterns = [
    path("", customer_dashboard, name="customer"),
    path("profile/", views.customer_profile, name="customer-profile"),
    path("my-orders/", views.my_orders, name="my-orders"),
    path(
        "order-details/<int:order_number>/", views.order_details, name="order-details"
    ),
]
