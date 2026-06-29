from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from .models import Course, Lesson
from users.models import Subscription


class LessonTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email="test@example.com",
            password="test1234"
        )
        self.course = Course.objects.create(
            name="Test Course",
            description="Test Description"
        )
        self.lesson_data = {
            "name": "Test Lesson",
            "description": "Test Description",
            "video_url": "https://youtube.com/watch?v=123",
            "course": self.course.id,
        }
        self.client.force_authenticate(user=self.user)

    def test_create_lesson(self):
        response = self.client.post("/api/lessons/", self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_lessons(self):
        Lesson.objects.create(
            name="Lesson 1",
            description="Desc 1",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user
        )
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_lesson(self):
        lesson = Lesson.objects.create(
            name="Lesson 1",
            description="Desc 1",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user
        )
        response = self.client.get(f"/api/lessons/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Lesson 1")

    def test_update_lesson(self):
        lesson = Lesson.objects.create(
            name="Lesson 1",
            description="Desc 1",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user
        )
        response = self.client.put(
            f"/api/lessons/{lesson.id}/",
            {
                "name": "Updated Lesson",
                "description": "Updated Desc",
                "video_url": "https://youtube.com/watch?v=456",
                "course": self.course.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson.refresh_from_db()
        self.assertEqual(lesson.name, "Updated Lesson")

    def test_delete_lesson(self):
        lesson = Lesson.objects.create(
            name="Lesson 1",
            description="Desc 1",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user
        )
        response = self.client.delete(f"/api/lessons/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_create_lesson_invalid_url(self):
        data = self.lesson_data.copy()
        data["video_url"] = "https://vk.com/video"
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="test1234")
        self.course = Course.objects.create(name="Test Course", description="Test Description")
        self.client.force_authenticate(user=self.user)

    def test_add_subscription(self):
        response = self.client.post("/api/users/subscriptions/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_delete_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post("/api/users/subscriptions/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())