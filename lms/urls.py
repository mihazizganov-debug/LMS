from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", views.LessonListCreateView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", views.LessonRetrieveUpdateDestroyView.as_view(), name="lesson-detail"),
]
