from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class IsCookieAuthenticated(BasePermission):
    """Prueft, ob der User ein gueltiges Access-Token im Cookie besitzt."""

    def has_permission(self, request, view) -> bool:
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return False
        try:
            authenticator = JWTAuthentication()
            validated_token = authenticator.get_validated_token(access_token)
            request.user = authenticator.get_user(validated_token)
            return True
        except (InvalidToken, TokenError):
            return False
