from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model, kept close to Django's default with room to grow."""

    phone = models.CharField(max_length=32, blank=True)

    def __str__(self) -> str:
        return self.get_username()


class Address(models.Model):
    """Optional saved shipping address for a user."""

    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=120, default="Ukraine")
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self) -> str:
        return f"{self.full_name}, {self.city}, {self.line1}"
