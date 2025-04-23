import csv
import io
import re
import logging
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from django.template import Template, Context
from django.conf import settings
from django.utils import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

from .models import EmailCampaign, EmailLog

logger = logging.getLogger(__name__)


def parse_template_tags(html_content):
    """Extract template tags from HTML content."""
    pattern = r"{{(.*?)}}"
    return [tag.strip() for tag in re.findall(pattern, html_content)]


def send_email_via_gmail_api(credentials, to_email, subject, html_content):
    """Send email using Gmail API."""
    try:
        service = build("gmail", "v1", credentials=credentials)
        message = MIMEText(html_content, "html")
        message["to"] = to_email
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": encoded_message})
            .execute()
        )

        return True, send_message["id"]
    except HttpError as error:
        return False, str(error)


def process_email_task(
    row_data, email_field, template_html, subject, campaign_id, credentials
):
    """Process a single email task."""
    recipient_email = row_data.get(email_field)
    if not recipient_email:
        return False, "Missing email address"

    # Create template context from CSV row
    context_data = {}
    for key, value in row_data.items():
        context_data[key] = value

    # Render template with context
    template = Template(template_html)
    context = Context(context_data)
    html_content = template.render(context)

    # Send email using Gmail API
    success, message = send_email_via_gmail_api(
        credentials, recipient_email, subject, html_content
    )

    # Log the result
    email_log = EmailLog.objects.create(
        campaign_id=campaign_id,
        recipient_email=recipient_email,
        status="sent" if success else "failed",
        error_message=None if success else message,
        sent_at=timezone.now() if success else None,
    )

    return success, message


def process_campaign(campaign_id, max_workers=10):
    """Process an email campaign with ThreadPoolExecutor."""
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        campaign.status = "processing"
        campaign.save()

        # Get user's credentials
        user = campaign.user
        google_profile = user.googleprofile

        credentials = Credentials(
            token=google_profile.access_token,
            refresh_token=google_profile.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE,
        )

        # Read CSV file
        csv_file = campaign.csv_file.open("r")
        reader = csv.DictReader(io.StringIO(csv_file.read().decode("utf-8")))
        rows = list(reader)
        campaign.total_emails = len(rows)
        campaign.save()

        # Get template content
        template_html = campaign.template.html_content

        # Process emails using ThreadPoolExecutor
        successful = 0
        failed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for row in rows:
                future = executor.submit(
                    process_email_task,
                    row,
                    campaign.email_field,
                    template_html,
                    campaign.subject,
                    campaign.id,
                    credentials,
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                success, _ = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1

                # Update campaign progress
                campaign.sent_emails = successful
                campaign.failed_emails = failed
                campaign.save()

        # Update campaign status
        campaign.status = "completed"
        campaign.save()

        return True
    except Exception as e:
        logger.error(f"Error processing campaign {campaign_id}: {str(e)}")
        # Update campaign status to failed
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
            campaign.status = "failed"
            campaign.save()
        except:
            pass
        return False
