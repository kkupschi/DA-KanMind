from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from kanban_app.models import Board
from .serializers import BoardSerializer


class BoardListCreateView(generics.ListCreateAPIView):
    """Lists boards the user owns or is a member of, and creates new boards."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()
