from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import User, Product
from .serializers import UserSerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # check if email already exists
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class UserSelfView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own products
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        # Ensure only owner can update
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("You do not have permission to edit this product.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure only owner can delete
        if instance.owner != self.request.user:
            raise PermissionDenied("You do not have permission to delete this product.")
        instance.delete()