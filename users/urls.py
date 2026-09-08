from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.WebLoginView.as_view(), name="login"),
    path("logout/", views.WebLogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("password/", views.change_password, name="change_password"),
    path("addresses/add/", views.add_address, name="add_address"),
]
