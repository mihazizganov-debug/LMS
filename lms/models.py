from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    preview = models.ImageField(
        upload_to="courses/",
        null=True,
        blank=True,
        verbose_name="Превью"
    )
    description = models.TextField(verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Владелец",
    )
    price = models.DecimalField(  # НОВОЕ ПОЛЕ
        max_digits=10,
        decimal_places=2,
        default=1000.00,
        verbose_name="Цена"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(verbose_name="описание")
    preview = models.ImageField(
        upload_to="lessons/",
        blank=True,
        null=True,
        verbose_name="превью"
    )
    video_url = models.URLField(verbose_name="ссылка на видео")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.name
