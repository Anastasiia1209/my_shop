from __future__ import annotations


from rest_framework import serializers

from products.models import Product
from products.serializers import ProductListSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "subtotal"]


class OrderCreateItemSerializer(serializers.Serializer):
    """Not used directly — orders are created from the session cart."""


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_method",
            "total_price",
            "full_name",
            "email",
            "phone",
            "shipping_address",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "total_price", "created_at", "updated_at"]


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Restricted update: a customer may only cancel a pending order."""

    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value: str) -> str:
        if value != Order.Status.CANCELLED:
            raise serializers.ValidationError(
                "Клієнт може лише скасувати замовлення (status=cancelled)."
            )
        if self.instance and self.instance.status != Order.Status.PENDING:
            raise serializers.ValidationError(
                "Можна скасувати лише замовлення зі статусом 'pending'."
            )
        return value


# ---------------------------------------------------------------------------
# Cart (session-based, exposed for API convenience)
# ---------------------------------------------------------------------------
class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField(source="product.name", read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def validate_product_id(self, value: int) -> int:
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Товар не знайдено.")
        return value
