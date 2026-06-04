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
