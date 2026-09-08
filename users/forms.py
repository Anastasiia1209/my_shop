from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Address, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже зареєстрований.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["full_name", "line1", "line2", "city", "postal_code", "country", "is_default"]
