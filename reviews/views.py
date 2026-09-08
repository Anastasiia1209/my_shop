from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from products.models import Product

from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a product, or submit a new one (requires a completed purchase)."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_product(self) -> Product:
        return get_object_or_404(Product, slug=self.kwargs["product_slug"])

    def get_queryset(self):
        return Review.objects.filter(product=self.get_product()).select_related("user")

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["product"] = self.get_product()
        return context

    def perform_create(self, serializer: ReviewSerializer) -> None:
        serializer.save(product=self.get_product(), user=self.request.user)
