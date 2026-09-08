from rest_framework.routers import DefaultRouter

from .api import CartAPIView, OrderViewSet
from django.urls import path

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="api-order")

urlpatterns = [
    path("cart/", CartAPIView.as_view(), name="api-cart"),
] + router.urls
