from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from kanban_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer
from .permissions import IsBoardMemberOrOwner

class BoardListCreateView(generics.ListCreateAPIView):
    """Lists boards the user owns or is a member of, and creates new boards."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

class BoardDetailView(generics.RetrieveAPIView):
    """Returns a single board with its members and tasks."""

    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
    lookup_url_kwarg = "board_id"