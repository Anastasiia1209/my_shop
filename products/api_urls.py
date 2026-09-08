from rest_framework.routers import DefaultRouter

from .api import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="api-category")
router.register("", ProductViewSet, basename="api-product")

urlpatterns = router.urls
