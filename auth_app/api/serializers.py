"""Serializers for authentication: registration, login and users."""
from django.contrib.auth import authenticate
from rest_framework import serializers
from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates registration data and creates a new user."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Ensure the email is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Ensure the password and its repetition match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create the user from the validated data."""
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates login credentials via email and password."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user and attach it to the data."""
        user = authenticate(
            username=attrs["email"], password=attrs["password"]
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializes basic public user information."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
