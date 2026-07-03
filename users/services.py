import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_name):
    """Создание продукта в Stripe"""
    try:
        product = stripe.Product.create(name=course_name, type="service")
        return product.id
    except Exception as e:
        raise ValidationError(f"Ошибка создания продукта: {str(e)}")


def create_stripe_price(amount, product_id):
    """Создание цены в Stripe (сумма в копейках)"""
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # переводим в копейки
            currency="rub",
        )
        return price.id
    except Exception as e:
        raise ValidationError(f"Ошибка создания цены: {str(e)}")


def create_stripe_session(price_id, success_url, cancel_url):
    """Создание сессии для оплаты"""
    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.id, session.url
    except Exception as e:
        raise ValidationError(f"Ошибка создания сессии: {str(e)}")


def get_stripe_session_status(session_id):
    """Получение статуса сессии"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except Exception as e:
        raise ValidationError(f"Ошибка получения статуса: {str(e)}")
