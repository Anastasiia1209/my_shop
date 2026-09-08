from django.urls import path

from .views import ReviewListCreateView

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="api-review-list-create"),
]
