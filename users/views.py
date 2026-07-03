from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course

from .models import Payment, Subscription, User
from .serializers import (PaymentSerializer, UserCreateSerializer,
                          UserSerializer)
from .services import (create_stripe_price, create_stripe_product,
                       create_stripe_session)


class PaymentFilter(filters.FilterSet):
    course = filters.NumberFilter(field_name="course__id")
    lesson = filters.NumberFilter(field_name="lesson__id")
    payment_method = filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)

    class Meta:
        model = Payment
        fields = ["course", "lesson", "payment_method"]


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
    permission_classes = [IsAuthenticated]


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message})


# 🔵 НОВЫЙ КЛАСС ДЛЯ ОПЛАТЫ ЧЕРЕЗ STRIPE
class PaymentCreateView(APIView):
    """Создание платежа через Stripe"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Создаём продукт в Stripe
        product_id = create_stripe_product(course.name)

        # Создаём цену в Stripe (например, 1000 руб)
        amount = 1000
        price_id = create_stripe_price(amount, product_id)

        # Создаём сессию
        session_id, payment_url = create_stripe_session(
            price_id=price_id,
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )

        # Сохраняем в БД
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            payment_method="transfer",
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_id,
            payment_url=payment_url,
            status="pending",
        )

        return Response(
            {
                "payment_id": payment.id,
                "payment_url": payment_url,
                "amount": amount,
                "course": course.name,
            },
            status=status.HTTP_201_CREATED,
        )


def payment_success(request):
    return HttpResponse("Оплата прошла успешно! Спасибо!")
