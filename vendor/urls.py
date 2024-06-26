from django.urls import path

from accounts import views as accounts_views

from . import views

urlpatterns = [
    path("", accounts_views.vendor_dashboard, name="vendor"),
    path("profile/", views.vendor_profile, name="vendor-profile"),
    path("menu-builder/", views.menu_builder, name="menu-builder"),
    # Category CRUD
    path("menu-builder/category/add/", views.add_category, name="add-category"),
    path(
        "menu-builder/category/edit/<slug:slug>/",
        views.edit_category,
        name="edit-category",
    ),
    path(
        "menu-builder/category/delete/<slug:slug>/",
        views.delete_category,
        name="delete-category",
    ),
    path(
        "menu-builder/category/<slug:slug>/",
        views.menu_builder_category,
        name="menu-builder-category",
    ),
    # Food Item CRUD
    path("menu-builder/food/add/", views.add_food, name="add-food"),
    path("menu-builder/food/edit/<slug:slug>/", views.edit_food, name="edit-food"),
    path(
        "menu-builder/food/delete/<slug:slug>/", views.delete_food, name="delete-food"
    ),
    # Opening Hour CRUD:
    path("opening-hour/", views.opening_hour, name="opening-hour"),
    path("opening-hour/add/", views.add_opening_hour, name="add-opening-hour"),
    path(
        "opening-hour/delete/<int:id>",
        views.delete_opening_hour,
        name="delete-opening-hour",
    ),
    path(
        "order-details/<int:order_number>/",
        views.order_details,
        name="vendor-order-details",
    ),
    path("my-orders/", views.my_orders, name="vendor-my-orders"),
]
