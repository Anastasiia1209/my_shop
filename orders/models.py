from __future__ import annotations

from django.conf import settings
from django.db import models


class Order(models.Model):
    """A customer order created from the cart at checkout."""

    class Status(models.TextChoices):
        PENDING = "pending", "Очікує оплати"
        PAID = "paid", "Оплачено"
        SHIPPED = "shipped", "Відправлено"
        DELIVERED = "delivered", "Доставлено"
        CANCELLED = "cancelled", "Скасовано"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Картка (мок)"
        CASH_ON_DELIVERY = "cod", "Оплата при отриманні"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CARD
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    shipping_address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.user})"

    def recalculate_total(self) -> None:
        total = sum((item.price * item.quantity for item in self.items.all()), start=0)
        self.total_price = total
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    """A single product line within an order, with a price snapshot."""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product", related_name="order_items", on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
