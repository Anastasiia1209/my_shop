from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Order


def send_order_confirmation_emails(order: Order) -> None:
    """Notify both the customer and the shop administrator about a new order."""
    context = {"order": order, "items": order.items.select_related("product").all()}

    customer_body = render_to_string("orders/email/order_confirmation.txt", context)
    send_mail(
        subject=f"Ваше замовлення №{order.pk} прийнято — Hop & Barley",
        message=customer_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=True,
    )

    admin_body = render_to_string("orders/email/order_admin_notification.txt", context)
    send_mail(
        subject=f"Нове замовлення №{order.pk}",
        message=admin_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )
