from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserListView.as_view(), name="user-list"),
    path("create/", views.UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("payments/", views.PaymentListView.as_view(), name="payment-list"),
    path("subscriptions/", views.SubscriptionView.as_view(), name="subscription"),
]
