from __future__ import annotations

from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    """Contact and shipping details collected at checkout."""

    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "shipping_address", "payment_method"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_phone(self) -> str:
        phone = self.cleaned_data.get("phone", "")
        digits = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if phone and len(digits) < 7:
            raise forms.ValidationError("Введіть коректний номер телефону.")
        return phone
