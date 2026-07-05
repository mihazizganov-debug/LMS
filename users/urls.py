from django.urls import path
from .views import (
    PaymentCreateView,
    PaymentListView,
    PaymentStatusView,
    SubscriptionView,
    UserCreateView,
    UserDetailView,
    UserListView,
)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("payments/create/", PaymentCreateView.as_view(), name="payment-create"),
    path("payments/status/", PaymentStatusView.as_view(), name="payment-status"),
    path("subscriptions/", SubscriptionView.as_view(), name="subscription"),
]
