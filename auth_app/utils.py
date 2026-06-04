from django.contrib.auth.models import User


def validate_registration_payload(data: dict) -> str | None:
    """Validiert die Registrierungsdaten und liefert Fehlertexte."""
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
    """Extrahiert die erste Fehlermeldung aus den Serializer-Fehlern als Text."""
    if "detail" in errors:
        error_data = errors["detail"]
        return error_data[0] if isinstance(error_data, list) else error_data

    for field, field_errors in errors.items():
        if isinstance(field_errors, list) and field_errors:
            return field_errors[0]

    return "Ungültige Daten."


from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens_for_user(user) -> dict:
    """Generiert ein Zugriffs- und ein Refresh-Token fuer den User."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_auth_cookies(response, tokens: dict) -> None:
    """Setzt das Access- und Refresh-Token als sichere HttpOnly-Cookies."""
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
