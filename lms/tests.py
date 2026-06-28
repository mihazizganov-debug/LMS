from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User

from .models import Course


class LessonTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="test1234")
        self.course = Course.objects.create(name="Test Course", description="Test Description")
        self.lesson_data = {
            "name": "Test Lesson",
            "description": "Test Description",
            "video_url": "https://youtube.com/watch?v=123",
            "course": self.course.id,
        }

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/lessons/", self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_invalid_url(self):
        self.client.force_authenticate(user=self.user)
        data = self.lesson_data.copy()
        data["video_url"] = "https://vk.com/video"
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/users/subscriptions/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
