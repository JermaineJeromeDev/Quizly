import pytest
from django.contrib.auth.models import User
from rest_framework import serializers


class UserRegisterSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate(self, attrs: dict) -> dict:
        """Prüft, ob die Passwörter übereinstimmen und die E-Mail einzigartig ist."""
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
        """Erstellt den Benutzer sicher mit gehashtem Passwort."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)
