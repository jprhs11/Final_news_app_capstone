# news_app1/permissions.py
from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    """
    Allows access only to users with the 'Journalist' role.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            (user.role == 'Journalist' or user.is_superuser)
        )


class IsEditor(permissions.BasePermission):
    """
    Allows access only to users with the 'Editor' role.
    """
    def has_permission(self, request, view):
        # Checks for capitalized 'Editor' to match your updated models.py
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            (user.role == 'Editor' or user.is_superuser)
        )


class IsReader(permissions.BasePermission):
    """
    Allows access only to users with the 'Reader' role.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            user.role == 'Reader'
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow authors to edit, but let Editors override for moderation.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow if user is the author OR if they have the Editor role
        user = request.user
        return bool(
            obj.author == user or
            user.role == 'Editor' or
            user.is_superuser
        )

