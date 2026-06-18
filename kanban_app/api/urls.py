from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    BoardViewSet,
    TaskViewSet,
    AssignedToMeView,
    ReviewingView,
)

router = SimpleRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(), name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="tasks-reviewing"),
    path("", include(router.urls)),
]
