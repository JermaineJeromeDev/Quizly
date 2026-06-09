from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def validate_registration_payload(data: dict) -> str | None:
    """Validate user registration inputs and return matching localized error messages if invalid."""
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirmed = data.get("confirmed_password")

    if not all([username, email, password, confirmed]):
        return "Ungültige Daten."
    if password != confirmed:
        return "Passwörter stimmen nicht überein."
    if (
        User.objects.filter(username=username).exists()
        or User.objects.filter(email=email).exists()
    ):
        return "Username oder E-Mail existiert bereits."
    return None


def extract_serializer_error(errors: dict) -> str:
    """Extract and flatten the first available validation error message string from serializer errors."""
    if "detail" in errors:
        error_data = errors["detail"]
        return error_data[0] if isinstance(error_data, list) else error_data

    for field, field_errors in errors.items():
        if isinstance(field_errors, list) and field_errors:
            return field_errors[0]

    return "Ungültige Daten."


def generate_tokens_for_user(user) -> dict:
    """Generate a fresh pair of access and refresh JWT strings for the specified user instance."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_auth_cookies(response, tokens: dict) -> None:
    """Attach the generated JWT access and refresh tokens to the HTTP response as secure HTTP-Only cookies."""
    response.set_cookie(
        key="access_token",
        value=tokens["access"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=900,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=604800,
    )


def delete_auth_cookies(response) -> None:
    """Remove authorization access and refresh tokens from the client browser environment by clearing cookies."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
