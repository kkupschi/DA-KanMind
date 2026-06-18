from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from kanban_app.models import Board
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
)
from .permissions import IsBoardMemberOrOwner, IsBoardOwner

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
