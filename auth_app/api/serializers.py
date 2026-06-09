import pytest
from django.contrib.auth.models import User
from rest_framework import serializers


class UserRegisterSerializer(serializers.ModelSerializer):
    """Handle user registration input validation and secure user profile creation."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate(self, attrs: dict) -> dict:
        """Verify that password fields match and the provided email address is unique."""
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"detail": "Passwörter stimmen nicht überein."}
            )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"detail": "Username oder E-Mail existiert bereits."}
            )

        return attrs

    def create(self, validated_data: dict) -> User:
        """Persist a new user instance securely in the database with a hashed password."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Validate user credentials payload supplied during authentication login requests."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
