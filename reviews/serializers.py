from __future__ import annotations

from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "product", "user", "created_at"]

    def validate(self, attrs: dict) -> dict:
        request = self.context["request"]
        product = self.context["product"]
        user = request.user

        from orders.models import OrderItem

        purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status__in=["paid", "shipped", "delivered"],
        ).exists()
        if not purchased:
            raise serializers.ValidationError(
                "Залишити відгук можна лише після покупки цього товару."
            )
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("Ви вже залишили відгук на цей товар.")
        return attrs
