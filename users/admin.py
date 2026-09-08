from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Додатково", {"fields": ("phone",)}),
    )
    list_display = ["username", "email", "phone", "is_staff", "is_active"]
    search_fields = ["username", "email", "phone"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "city", "is_default"]
    search_fields = ["user__username", "full_name", "city"]
