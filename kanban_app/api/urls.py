from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BoardViewSet

router = SimpleRouter()
router.register(r"boards", BoardViewSet, basename="board")

urlpatterns = [
    path("", include(router.urls)),
]
