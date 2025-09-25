from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import User, Product, HealthCheck
from .serializers import UserSerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.permissions import SAFE_METHODS, BasePermission

@csrf_exempt
@require_http_methods(["GET"])  # only allow GET
def healthz(request):
    # Reject if request has a body
    if request.method == "GET" and request.body:
        return HttpResponse(status=400)

    # Reject if query params are passed
    if request.GET:
        return HttpResponse(status=400)

    try:
        HealthCheck.objects.create()
        response = HttpResponse(status=200)
    except DatabaseError:
        response = HttpResponse(status=503)

    # Required headers
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"

    return response


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        if not email:
            raise ValidationError({"email": "This field is required."})

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        user = User.objects.get(email=email)

        token, created = Token.objects.get_or_create(user=user)

        headers = self.get_success_headers(serializer.data)

        response_data = serializer.data
        response_data["token"] = token.key

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)




class UserSelfView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Disallow updates to email or account timestamps
        disallowed_fields = {"email", "account_created", "account_updated"}
        if any(field in request.data for field in disallowed_fields):
            return Response(
                {"error": "You can only update first_name, last_name, or password."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read-only (GET, HEAD, OPTIONS) always allowed
        if request.method in SAFE_METHODS:
            return True
        # Write (PATCH, PUT, DELETE) only for owner
        return obj.owner == request.user


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ["get", "put", "patch", "delete"]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().owner:
            raise PermissionDenied("You can only update your own products.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied("You do not have permission to delete this product.")
        instance.delete()

class BasicAuthOnlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.email}, you are authenticated!"})

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch"]

    def get_object(self):
        user = super().get_object()
        # Prevent users from accessing/updating others
        if self.request.user != user:
            raise PermissionDenied("You cannot access this user.")
        return user

    def update(self, request, *args, **kwargs):
        # Disallow updates to restricted fields
        disallowed_fields = {"email", "account_created", "account_updated"}
        if any(field in request.data for field in disallowed_fields):
            return Response(
                {"error": "You can only update first_name, last_name, or password."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

