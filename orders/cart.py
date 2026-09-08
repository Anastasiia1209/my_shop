from __future__ import annotations

from decimal import Decimal
from typing import Iterator

from django.conf import settings
from django.http import HttpRequest

from products.models import Product


class Cart:
    """A shopping cart stored in the user's session.

    Session layout: {"<product_id>": {"quantity": int, "price": str}}
    """

    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: dict[str, dict[str, str]] = cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        max_qty = product.stock
        if self.cart[product_id]["quantity"] > max_qty:
            self.cart[product_id]["quantity"] = max_qty
        if self.cart[product_id]["quantity"] <= 0:
            self.remove(product)
        else:
            self.save()

    def save(self) -> None:
        self.session.modified = True

    def remove(self, product: Product) -> None:
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self) -> None:
        self.session[settings.CART_SESSION_ID] = {}
        self.save()

    def __iter__(self) -> Iterator[dict]:
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if product is None:
                continue
            price = Decimal(item["price"])
            quantity = int(item["quantity"])
            yield {
                "product": product,
                "quantity": quantity,
                "price": price,
                "subtotal": price * quantity,
            }

    def __len__(self) -> int:
        return sum(int(item["quantity"]) for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        return sum(
            (Decimal(item["price"]) * int(item["quantity"]) for item in self.cart.values()),
            start=Decimal("0"),
        )
