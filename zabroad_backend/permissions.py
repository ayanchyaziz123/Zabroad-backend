from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: read is open; write requires being the owner.
    Expects the model instance to have a `posted_by` or `user` field.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = (
            getattr(obj, 'author', None) or
            getattr(obj, 'posted_by', None) or
            getattr(obj, 'user', None)
        )
        return owner == request.user


class IsOwner(permissions.BasePermission):
    """Full block — any access requires ownership."""

    def has_object_permission(self, request, view, obj):
        owner = (
            getattr(obj, 'author', None) or
            getattr(obj, 'posted_by', None) or
            getattr(obj, 'user', None)
        )
        return owner == request.user
