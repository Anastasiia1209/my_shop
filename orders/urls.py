from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("account/orders/", views.order_history, name="order_history"),
    path("account/orders/<int:order_id>/", views.order_detail, name="order_detail"),
]
