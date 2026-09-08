from __future__ import annotations

from rest_framework import permissions, viewsets

from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Only staff users may create/update/delete products or categories."""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    """
    Browse the product catalog.

    Supports search (`?search=`), ordering (`?ordering=price,-created_at`)
    and filtering by category/price range via `ProductFilter`.
    """

    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Product.objects.select_related("category").with_rating()
        if self.request.user.is_staff:
            return qs
        return qs.active()

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
