"""API views for the kanban app's boards, tasks and comments."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from .permissions import (
    IsBoardMemberOrOwner, IsBoardOwner, IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner, IsCommentAuthor,
)
from .serializers import (
    BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer,
    TaskSerializer, CommentSerializer,
)


class BoardViewSet(viewsets.ModelViewSet):
    """Provides list, create, retrieve, update and delete for boards."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Return the user's boards when listing, all boards otherwise."""
        if self.action == "list":
            user = self.request.user
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()
        return Board.objects.all()

    def get_serializer_class(self):
        """Return the serializer matching the current action."""
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardSerializer

    def get_permissions(self):
        """Return permissions matching the current action."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        if self.action in ("retrieve", "partial_update"):
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return [IsAuthenticated()]


class TaskViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    """Provides create, update and delete for tasks."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ["post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """Return permissions matching the current action."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        if self.action == "partial_update":
            return [IsAuthenticated(), IsTaskBoardMember()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Create a task after checking board existence and membership."""
        board = get_object_or_404(Board, pk=request.data.get("board"))
        user = request.user
        is_member = board.members.filter(id=user.id).exists()
        if board.owner != user and not is_member:
            raise PermissionDenied()
        return super().create(request, *args, **kwargs)


class AssignedToMeView(generics.ListAPIView):
    """Lists tasks where the current user is the assignee."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks assigned to the current user."""
        return Task.objects.filter(assignee=self.request.user)


class ReviewingView(generics.ListAPIView):
    """Lists tasks where the current user is the reviewer."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks the current user reviews."""
        return Task.objects.filter(reviewer=self.request.user)


class CommentListCreateView(generics.ListCreateAPIView):
    """Lists and creates comments for a task accessible to board members."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        """Return the task if the user is a board member, else deny."""
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        user = self.request.user
        board = task.board
        is_member = board.members.filter(id=user.id).exists()
        if board.owner != user and not is_member:
            raise PermissionDenied()
        return task

    def get_queryset(self):
        """Return the comments of the requested task."""
        return self.get_task().comments.all()

    def perform_create(self, serializer):
        """Save the comment with the request user as author."""
        serializer.save(author=self.request.user, task=self.get_task())


class CommentDestroyView(generics.DestroyAPIView):
    """Deletes a comment; only the comment author is allowed."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        """Return the comment after checking author permission."""
        comment = get_object_or_404(
            Comment, pk=self.kwargs["comment_id"],
            task_id=self.kwargs["task_id"],
        )
        self.check_object_permissions(self.request, comment)
        return comment
