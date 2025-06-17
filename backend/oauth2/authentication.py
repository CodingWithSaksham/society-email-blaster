import requests
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

User = get_user_model()


class GoogleTokenAuthentication(BaseAuthentication):
    """
    DRF Authentication class that:
    - Reads 'Authorization: Bearer <token>' header
    - Validates it against Google’s userinfo endpoint
    - Returns (user, token) if valid
    """

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None  # we’re not handling this request

        token = auth.split(" ", 1)[1].strip()
        if not token:
            raise exceptions.AuthenticationFailed("Empty Bearer token")

        # hit Google
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code != 200:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        data = resp.json()
        email = data.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("No email in token")

        # lookup the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No user matches this token")

        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
