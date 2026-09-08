from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .emails import send_order_confirmation_emails
from .forms import CheckoutForm
from .models import Order, OrderItem


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        messages.error(request, "Кількість має бути більшою за нуль.")
        return redirect(product.get_absolute_url())

    if quantity > product.stock:
        messages.warning(
            request, f"На складі доступно лише {product.stock} шт. «{product.name}»."
        )
        quantity = product.stock

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"«{product.name}» додано до кошика.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"«{product.name}» видалено з кошика.")
    return redirect("orders:cart_detail")


class CheckoutView(LoginRequiredMixin, View):
    """Handles order creation from the current session cart. Requires login."""

    template_name = "orders/checkout.html"
    login_url = "users:login"

    @staticmethod
    def _initial_data(request: HttpRequest) -> dict:
        user = request.user
        if user.is_authenticated:
            return {
                "full_name": user.get_full_name() or user.username,
                "email": user.email,
                "phone": getattr(user, "phone", ""),
            }
        return {}

    def get(self, request: HttpRequest) -> HttpResponse:
        cart = Cart(request)
        if len(cart) == 0:
            messages.warning(request, "Ваш кошик порожній.")
            return redirect("orders:cart_detail")
        form = CheckoutForm(initial=self._initial_data(request))
        return render(request, self.template_name, {"form": form, "cart": cart})

    def post(self, request: HttpRequest) -> HttpResponse:
        cart = Cart(request)
        if len(cart) == 0:
            return redirect("orders:cart_detail")

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "cart": cart})

        with transaction.atomic():
            # Re-check stock inside the transaction to avoid overselling.
            for item in cart:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                if product.stock < item["quantity"]:
                    messages.error(
                        request,
                        f"Недостатньо товару «{product.name}» на складі "
                        f"(доступно {product.stock}).",
                    )
                    return render(request, self.template_name, {"form": form, "cart": cart})

            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

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
        messages.success(request, f"Замовлення №{order.pk} успішно оформлено!")
        return redirect("orders:order_detail", order_id=order.pk)


@login_required
def order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_history(request: HttpRequest) -> HttpResponse:
    status = request.GET.get("status")
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
    if status:
        orders = orders.filter(status=status)
    return render(
        request,
        "orders/order_history.html",
        {"orders": orders, "statuses": Order.Status.choices, "current_status": status},
    )
