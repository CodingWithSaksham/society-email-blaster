# This file handles the authorization of the user, for more info about
# Google's API read the documentation at
# https://developers.google.com/identity/protocols/oauth2/web-server#python_4

import requests
from os import path
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status

from social_django.models import UserSocialAuth
from datetime import timedelta
from google_auth_oauthlib.flow import Flow

from .models import GoogleCredential

CLIENT_SECRETS = path.join(path.dirname(__file__), "client_secrets.json")

User = get_user_model()


class GoogleAuthCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "Authorization code not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Set up the OAuth flow
            redirect_uri = request.build_absolute_uri(reverse("oauth2:callback"))
            flow = Flow.from_client_secrets_file(
                client_secrets_file=CLIENT_SECRETS,
                scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE,
                redirect_uri=redirect_uri,
            )

            # Exchange code for tokens
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # Get tokens and expiry
            access_token = credentials.token
            refresh_token = credentials.refresh_token
            token_expiry = (
                credentials.expiry
                if credentials.expiry
                else timezone.now() + timedelta(hours=1)
            )

            # Get user info from Google API
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            email = user_data.get("email")
            if not email:
                return Response(
                    {"error": "Email not found in Google profile"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Find or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user with standard User model
                username = f"google_{email.split('@')[0]}"
                # Check if username already exists, append numbers if needed
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                # Create the user
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=user_data.get("given_name", ""),
                    last_name=user_data.get("family_name", ""),
                )

                # Create social auth entry - user is now a User instance
                UserSocialAuth.objects.create(
                    user=user,  # This is now correctly a User instance
                    provider="google-oauth2",
                    uid=email,
                    extra_data={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "email": email,
                        "expires": token_expiry.timestamp() if token_expiry else None,
                    },
                )

            # Log the user in
            login(request, user)

            # Save Google credentials - CAREFUL here, don't assign the result to user
            # This returns (instance, created) tuple
            cred_instance, _ = GoogleCredential.objects.update_or_create(
                user=user,
                defaults={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_expiry": token_expiry,
                },
            )

            # Create DRF token
            token, _ = Token.objects.get_or_create(user=user)

            # For debugging, return token as JSON
            return Response(
                {"token": token.key, "user": user.username, "email": user.email},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"OAuth callback error: {e}")
            import traceback

            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthStatusView(APIView):
    def get(self, request):
        try:
            google_cred = GoogleCredential.objects.get(user=request.user)
            is_expired = google_cred.token_expiry < timezone.now()

            return Response(
                {
                    "authenticated": True,
                    "email": request.user.email,
                    "token_expired": is_expired,
                }
            )
        except GoogleCredential.DoesNotExist:
            return Response(
                {
                    "authenticated": False,
                    "email": request.user.email if request.user.email else None,
                    "token_expired": None,
                }
            )


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return the Google OAuth2 login URL for the frontend to redirect to
        """

        redirect_uri = request.build_absolute_uri(reverse("oauth2:callback"))
        flow = Flow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRETS,
            scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE,
        )
        flow.redirect_uri = redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        return Response({"login_url": authorization_url}, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    def get(self, request):
        """
        Return current user information
        """
        if not request.user.is_authenticated:
            return Response(
                {"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user has Google credentials
        has_google_credentials = False
        try:
            GoogleCredential.objects.get(user=request.user)
            has_google_credentials = True
        except GoogleCredential.DoesNotExist:
            pass

        return Response(
            {
                "authenticated": True,
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "has_google_credentials": has_google_credentials,
            },
            status=status.HTTP_200_OK,
        )
