# This file handles the authorization of the user, for more info about
# Google's API read the documentation at
# https://developers.google.com/identity/protocols/oauth2/web-server#python_4

from os import path, environ
from typing import Optional, Dict, Any

from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.request import Request

import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow

from .models import GoogleProfile

if settings.DEBUG:
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRET_FILE = path.join(path.dirname(__file__), "client_secrets.json")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
]
REDIRECT_URI = "http://localhost:8000/auth/callback/"


class GoogleAuthInit(APIView):
    def get(self, request: Request, *args, **kwargs):
        # Create flow instance to manage Google's OAuth2 flow steps
        flow: Flow = Flow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRET_FILE, scopes=SCOPES
        )

        flow.redirect_uri = REDIRECT_URI
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )
        request.session["state"] = state

        return redirect(authorization_url)


class GoogleAuthCallback(APIView):
    def get(self, request: Request):
        state: Optional[str] = request.session.get("state")
        if state is None:
            return JsonResponse({"error": "State missing"}, status=400)

        flow: Flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = REDIRECT_URI

        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials: google.oauth2.credentials.Credentials = flow.credentials

        # Store credentials in session
        request.session["credentials"] = credentials_to_dict(credentials)

        # Store credentials in database
        if request.user.is_authenticated:
            profile, created = GoogleProfile.objects.get_or_create(user=request.user)

            profile.access_token = credentials.token
            profile.refresh_token = credentials.refresh_token
            profile.token_expiry = credentials.expiry
            profile.save()

        # TODO: Redirect to home page or tell frontend
        # to redirect user if authentication was successful

        # return JsonResponse({"success": True})
        return redirect("home")


def credentials_to_dict(credentials) -> Dict[str, Any]:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
