from rest_framework.permissions import BasePermission

class IsBoardMemberOrOwner(BasePermission):
    """Allows access only to board owners or members."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(id=user.id).exists()