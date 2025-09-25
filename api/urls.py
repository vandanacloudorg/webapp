from django.urls import path
from .views import UserCreateView, UserSelfView, UserDetailView, ProductCreateView, ProductDetailView, healthz, BasicAuthOnlyView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    path("healthz", healthz, name="healthz"),

    # User endpoints
    path("v1/user/", UserCreateView.as_view(), name="user-create"),
    path("v1/user/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path('v1/user/self/', UserSelfView.as_view(), name='user-detail'),

    # Product endpoints
    path("v1/product/", ProductCreateView.as_view(), name="product-create"),
    path("v1/product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),

    path("v1/token/", obtain_auth_token, name="api_token_auth"),
    path("v1/basic-auth/", BasicAuthOnlyView.as_view(), name="basic_auth_test"),
]