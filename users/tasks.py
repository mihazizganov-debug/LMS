from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import User, Subscription
from lms.models import Course


@shared_task
def send_course_update_email(course_id):
    """Отправка писем подписчикам об обновлении курса"""
    course = Course.objects.get(id=course_id)
    subscribers = Subscription.objects.filter(course=course).select_related('user')

    for subscription in subscribers:
        send_mail(
            subject=f'Обновление курса: {course.name}',
            message=f'Курс "{course.name}" был обновлён!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.user.email],
            fail_silently=False,
        )
    return f'Отправлено писем: {subscribers.count()}'


@shared_task
def deactivate_inactive_users():
    """Блокировка пользователей, которые не заходили более месяца"""
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True
    )
    count = inactive_users.count()
    inactive_users.update(is_active=False)
    return f'Заблокировано пользователей: {count}'
