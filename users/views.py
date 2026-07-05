from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from .models import Payment, Subscription, User
from .serializers import (
    PaymentSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from .services import (
    StripeAPIException,
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_stripe_session_status,
)


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


class PaymentCreateView(APIView):
    """Создание платежа через Stripe"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создание платежа для оплаты курса через Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course_id"],
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID курса, который пользователь хочет оплатить",
                ),
            },
            example={"course_id": 1},
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="ID платежа в системе"
                    ),
                    "payment_url": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Ссылка на оплату в Stripe"
                    ),
                    "amount": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="Сумма в рублях"
                    ),
                    "course": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Название курса"
                    ),
                },
                example={
                    "payment_id": 1,
                    "payment_url": "https://checkout.stripe.com/...",
                    "amount": 1000,
                    "course": "Тестовый курс",
                },
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                examples={
                    "application/json": {"error": "course_id обязателен"}
                },
            ),
            401: "Не авторизован",
            404: "Курс не найден",
            500: "Ошибка Stripe",
        },
    )
    def post(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)

        # Берём цену из курса
        amount = getattr(course, "price", 1000)

        try:
            product_id = create_stripe_product(course.name)
            price_id = create_stripe_price(amount, product_id)
            session_id, payment_url = create_stripe_session(
                price_id=price_id,
                success_url="http://localhost:8000/success/",
                cancel_url="http://localhost:8000/cancel/",
            )
        except StripeAPIException as e:
            return Response(
                {"error": str(e.detail)},
                status=e.status_code,
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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


class PaymentStatusView(APIView):
    """Проверка статуса платежа через Stripe"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Проверка статуса платежа через Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["payment_id"],
            properties={
                "payment_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID платежа в системе",
                ),
            },
            example={"payment_id": 1},
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="ID платежа"
                    ),
                    "status": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Статус платежа"
                    ),
                },
                example={"payment_id": 1, "status": "paid"},
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                examples={"application/json": {"error": "payment_id обязателен"}},
            ),
            401: "Не авторизован",
            404: "Платёж не найден",
            500: "Ошибка Stripe",
        },
    )
    def post(self, request):
        payment_id = request.data.get("payment_id")
        if not payment_id:
            return Response(
                {"error": "payment_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        try:
            status_from_stripe = get_stripe_session_status(payment.stripe_session_id)
            payment.status = status_from_stripe
            payment.save()
        except StripeAPIException as e:
            return Response(
                {"error": str(e.detail)},
                status=e.status_code,
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status,
            }
        )
