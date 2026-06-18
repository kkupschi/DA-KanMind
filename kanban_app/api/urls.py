from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    BoardViewSet, TaskViewSet, AssignedToMeView, ReviewingView,
    CommentListCreateView, CommentDestroyView,
)

router = SimpleRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(),
         name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(),
         name="tasks-reviewing"),
    path("tasks/<int:task_id>/comments/", CommentListCreateView.as_view(),
         name="task-comments"),
    path("tasks/<int:task_id>/comments/<int:comment_id>/",
         CommentDestroyView.as_view(), name="task-comment-detail"),
    path("", include(router.urls)),
]
