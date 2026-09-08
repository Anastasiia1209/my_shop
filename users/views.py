from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import update_session_auth_hash
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import AddressForm, ProfileForm, RegisterForm
from .models import Address


class WebLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


class WebLogoutView(LogoutView):
    next_page = reverse_lazy("products:catalog")


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("products:catalog")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Реєстрація успішна! Ласкаво просимо.")
            return redirect("products:catalog")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)
    addresses = Address.objects.filter(user=request.user)
    return render(request, "users/profile.html", {"form": form, "addresses": addresses})


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успішно змінено.")
            return redirect("users:profile")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


@login_required
def add_address(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            address.save()
            messages.success(request, "Адресу додано.")
            return redirect("users:profile")
    else:
        form = AddressForm()
    return render(request, "users/address_form.html", {"form": form})
