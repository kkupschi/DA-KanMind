from rest_framework.permissions import BasePermission

class IsBoardMemberOrOwner(BasePermission):
    """Allows access only to board owners or members."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(id=user.id).exists()

class IsBoardOwner(BasePermission):
    """Allows access only to the board owner."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsTaskBoardMember(BasePermission):
    """Allows access only to members or the owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(id=user.id).exists()

class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allows access only to the task creator or the owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or obj.board.owner == request.user