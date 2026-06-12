from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class User(AbstractUser):
    """Custom user using email as the login identifier."""

    username = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    objects = CustomUserManager()

    def __str__(self):
        return self.fullname