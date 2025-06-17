"""
Copyright 2019 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# [START gmail_send_message]
import os
import base64
from dotenv import load_dotenv
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

load_dotenv()

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
]


def gmail_send_message():
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds, _ = google.auth.default()
    # creds = Credentials(
    #     token="!IETnhF4dZKZzXEqOsLM92BSY19yznfZT8vOi4ycm",
    #     token_uri="https://oauth2.googleapis.com/token",
    #     client_id=SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
    #     client_secret=SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
    #     scopes=SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE,
    # )
    #
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content("This is automated draft mail")

        message["To"] = "sakshamthecoder@gmail.com"
        message["From"] = "sjain1_be24@thapar.edu"
        message["Subject"] = "Automated draft"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f"Message Id: {send_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


if __name__ == "__main__":
    gmail_send_message()
# [END gmail_send_message]
