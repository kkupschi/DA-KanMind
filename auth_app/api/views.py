from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status

from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    """Creates a new user and returns an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id,
        }
        return Response(data, status=status.HTTP_201_CREATED)