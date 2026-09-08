from __future__ import annotations

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Order


class IsOrderOwner(permissions.BasePermission):
    """Allows access only to the order's own owner."""

    def has_object_permission(self, request: Request, view: APIView, obj: Order) -> bool:
        return obj.user_id == request.user.id
