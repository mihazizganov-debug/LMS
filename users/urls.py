from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("payments/", views.PaymentListView.as_view(), name="payment-list"),
]
