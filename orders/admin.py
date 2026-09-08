from __future__ import annotations

from django.contrib import admin
from django.db.models import Avg, Count, QuerySet, Sum
from django.http import HttpRequest

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["price"]


@admin.action(description="Позначити як 'Відправлено'")
def mark_shipped(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(status=Order.Status.SHIPPED)


@admin.action(description="Позначити як 'Оплачено'")
def mark_paid(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(status=Order.Status.PAID)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "payment_method", "total_price", "created_at"]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["id", "user__username", "email", "full_name"]
    inlines = [OrderItemInline]
    actions = [mark_shipped, mark_paid]
    readonly_fields = ["total_price", "created_at", "updated_at"]

    def changelist_view(self, request: HttpRequest, extra_context: dict | None = None):
        """Inject revenue / order-count analytics above the order list."""
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        extra_context["analytics"] = qs.aggregate(
            total_revenue=Sum("total_price"),
            order_count=Count("id"),
            avg_order_value=Avg("total_price"),
        )
        top_products = (
            OrderItem.objects.values("product__name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )
        extra_context["top_products"] = top_products
        return super().changelist_view(request, extra_context=extra_context)
