from django.urls import path
from .views import UserCreateView, UserSelfView

urlpatterns = [
    path('v1/user/', UserCreateView.as_view(), name='user-create'),
    path('v1/user/self/', UserSelfView.as_view(), name='user-self'),
]
