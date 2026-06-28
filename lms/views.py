from rest_framework import generics, permissions, viewsets

from users.permissions import IsModerator, IsNotModerator, IsOwner

from .models import Course, Lesson
from .paginators import CoursePaginator, LessonPaginator
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модератор").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модератор").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [permissions.IsAuthenticated]
        elif self.request.method == "POST":
            permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модератор").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [permissions.IsAuthenticated]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.request.method == "DELETE":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
