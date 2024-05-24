from django.urls import path

from marketplace import views

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path("<slug:slug>/", views.vendor_details, name="vendor-details"),
    # Add To Cart
    path("add-to-cart/<int:food_id>/", views.add_to_cart, name="add-to-cart"),
    # Decrease from Cart
    path(
        "decrease-from-cart/<int:food_id>/",
        views.decrease_from_cart,
        name="decrease-from-cart",
    ),
    # Delete Cart Item
    path("delete-cart/<int:cart_id>/", views.delete_cart, name="delete-cart"),
]
