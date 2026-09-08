from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .cart import Cart
from .emails import send_order_confirmation_emails
from .models import Order, OrderItem
from .permissions import IsOrderOwner
from .serializers import CartItemSerializer, OrderSerializer, OrderUpdateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Create, list, retrieve, update (cancel) and delete the current user's orders.

    Orders are created from the contents of the caller's session cart.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return OrderUpdateSerializer
        return OrderSerializer

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        cart = Cart(request)
        if len(cart) == 0:
            return Response({"detail": "Кошик порожній."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        with transaction.atomic():
            for item in cart:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                if product.stock < item["quantity"]:
                    return Response(
                        {"detail": f"Недостатньо товару «{product.name}» на складі."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            default_full_name = request.user.get_full_name() or request.user.username
            order = Order.objects.create(
                user=request.user,
                full_name=data.get("full_name", default_full_name),
                email=data.get("email", request.user.email),
                phone=data.get("phone", ""),
                shipping_address=data.get("shipping_address", ""),
                payment_method=data.get("payment_method", Order.PaymentMethod.CARD),
                total_price=cart.get_total_price(),
            )
            for item in cart:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=item["price"],
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])

        cart.clear()
        send_order_confirmation_emails(order)
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer) -> None:
        serializer.save()

    def destroy(self, request: Request, *args: object, **kwargs: object) -> Response:
        order = self.get_object()
        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": "Можна видалити лише замовлення зі статусом 'pending'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartAPIView(APIView):
    """Manage the caller's session-based cart (GET, POST, PATCH, DELETE)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        cart = Cart(request)
        items = [
            {
                "product_id": entry["product"].id,
                "name": entry["product"].name,
                "quantity": entry["quantity"],
                "price": entry["price"],
                "subtotal": entry["subtotal"],
            }
            for entry in cart
        ]
        return Response({"items": items, "total_price": cart.get_total_price()})

    def post(self, request: Request) -> Response:
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
        cart = Cart(request)
        cart.add(product=product, quantity=serializer.validated_data["quantity"])
        return Response(status=status.HTTP_201_CREATED)

    def patch(self, request: Request) -> Response:
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
        cart = Cart(request)
        cart.add(
            product=product,
            quantity=serializer.validated_data["quantity"],
            override_quantity=True,
        )
        return Response(status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        product_id = request.data.get("product_id") or request.query_params.get("product_id")
        cart = Cart(request)
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            cart.remove(product)
        else:
            cart.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)
