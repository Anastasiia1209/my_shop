from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("product/<slug:slug>/", views.product_detail, name="detail"),
    path("product/<slug:slug>/review/", views.add_review, name="add_review"),
]
