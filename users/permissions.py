from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ только пользователям в группе 'Модератор'
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модератор').exists()


class IsOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
