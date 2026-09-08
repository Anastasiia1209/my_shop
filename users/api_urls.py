from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import AddressViewSet, MeView, RegisterView

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="api-address")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("login/", TokenObtainPairView.as_view(), name="api-login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="api-login-refresh"),
    path("me/", MeView.as_view(), name="api-me"),
] + router.urls
