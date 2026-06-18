from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from kanban_app.models import Board, Task
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
)
from .permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
)

class BoardViewSet(viewsets.ModelViewSet):
    """Provides list, create, retrieve, update and delete for boards."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()
        return Board.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        if self.action in ("retrieve", "partial_update"):
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return [IsAuthenticated()]

class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Provides create, update and delete for tasks."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ["post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        if self.action == "partial_update":
            return [IsAuthenticated(), IsTaskBoardMember()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        board = get_object_or_404(Board, pk=request.data.get("board"))
        user = request.user
        if board.owner != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied()
        return super().create(request, *args, **kwargs)

class AssignedToMeView(generics.ListAPIView):
    """Lists tasks where the current user is the assignee."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

class ReviewingView(generics.ListAPIView):
    """Lists tasks where the current user is the reviewer."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)
