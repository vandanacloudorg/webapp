from django.urls import path
from .views import UserCreateView, UserSelfView, ProductCreateView, ProductDetailView

urlpatterns = [
    path('v1/user/', UserCreateView.as_view(), name='user-create'),
    path('v1/user/self/', UserSelfView.as_view(), name='user-self'),

    #Product endpoints
    path('v1/product/', ProductCreateView.as_view(), name='product-create'),
    path('v1/product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
