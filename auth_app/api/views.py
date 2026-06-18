from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User
from .serializers import (
    RegistrationSerializer, LoginSerializer, UserSerializer,
)

class RegistrationView(APIView):
    """Creates a new user and returns an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key, "fullname": user.fullname,
            "email": user.email, "user_id": user.id,
        }
        return Response(data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """Authenticates a user and returns an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key, "fullname": user.fullname,
            "email": user.email, "user_id": user.id,
        }
        return Response(data, status=status.HTTP_200_OK)

class EmailCheckView(APIView):
    """Checks whether a user with the given email exists."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)