from auth_app.utils import extract_serializer_error
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserRegisterSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request) -> Response:
    """Registriert einen neuen Benutzer via Serializer."""
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        error_message = extract_serializer_error(serializer.errors)
        return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(
        {"detail": "User created successfully!"}, status=status.HTTP_201_CREATED
    )
