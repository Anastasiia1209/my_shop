from __future__ import annotations

from rest_framework import generics, permissions, viewsets

from .models import Address, User
from .serializers import AddressSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Public endpoint to create a new user account."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's own profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    """CRUD for the authenticated user's own saved addresses."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer: AddressSerializer) -> None:
        serializer.save(user=self.request.user)
