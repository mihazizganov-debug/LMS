import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeAPIException(APIException):
    """Исключение для ошибок Stripe"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Ошибка при обработке платежа'
    default_code = 'stripe_error'


def create_stripe_product(course_name):
    """Создание продукта в Stripe"""
    try:
        product = stripe.Product.create(
            name=course_name,
            type='service'
        )
        return product.id
    except stripe.error.StripeError as e:
        raise StripeAPIException(f'Ошибка создания продукта: {e.user_message}')
    except Exception as e:
        raise StripeAPIException(f'Неизвестная ошибка: {str(e)}')


def create_stripe_price(amount, product_id):
    """Создание цены в Stripe (сумма в копейках)"""
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),
            currency='rub',
        )
        return price.id
    except stripe.error.StripeError as e:
        raise StripeAPIException(f'Ошибка создания цены: {e.user_message}')
    except Exception as e:
        raise StripeAPIException(f'Неизвестная ошибка: {str(e)}')


def create_stripe_session(price_id, success_url, cancel_url):
    """Создание сессии для оплаты"""
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.id, session.url
    except stripe.error.StripeError as e:
        raise StripeAPIException(f'Ошибка создания сессии: {e.user_message}')
    except Exception as e:
        raise StripeAPIException(f'Неизвестная ошибка: {str(e)}')


def get_stripe_session_status(session_id):
    """Получение статуса сессии"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except stripe.error.StripeError as e:
        raise StripeAPIException(f'Ошибка получения статуса: {e.user_message}')
    except Exception as e:
        raise StripeAPIException(f'Неизвестная ошибка: {str(e)}')
