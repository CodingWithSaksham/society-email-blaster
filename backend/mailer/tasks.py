import pandas as pd
import logging
from celery import shared_task
from django.db import connection

from oauth2.models import GoogleCredential
from .models import EmailCampaign, EmailLog
from .utils import (
    parse_excel_file,
    validate_template_and_headers,
    replace_tags_in_template,
    send_email_with_gmail_api,
)

logger = logging.getLogger(__name__)


@shared_task
def process_email_campaign(campaign_id: int) -> str:
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        campaign.status = "processing"
        campaign.save()

        # Parse and validate
        df = parse_excel_file(campaign.excel_file.path)
        validate_template_and_headers(campaign.html_template, df)

        campaign.total_emails = len(df)
        campaign.save()

        # Loop through each row
        for idx, row in df.iterrows():
            # Ensure email exists
            email = next(
                (row.get(col) for col in df.columns if col.lower() == "email"), None
            )
            if pd.isna(email) or not email:
                EmailLog.objects.create(
                    campaign=campaign,
                    recipient_email="missing_email",
                    success=False,
                    error_message="Email missing in row",
                )
                campaign.failed_emails += 1
                campaign.save()
                continue

            html_content = replace_tags_in_template(campaign.html_template, row)
            success, error_msg = send_email_with_gmail_api(
                GoogleCredential.objects.get(user=campaign.user),
                email,
                campaign.subject,
                html_content,
            )

            EmailLog.objects.create(
                campaign=campaign,
                recipient_email=email,
                success=success,
                error_message=error_msg,
            )
            if success:
                campaign.sent_emails += 1
            else:
                campaign.failed_emails += 1
            campaign.save()

        campaign.status = "completed"
        campaign.save()
        summary = f"Completed campaign {campaign_id}: sent={campaign.sent_emails}, failed={campaign.failed_emails}"
        logger.info(summary)
        return summary

    except Exception as e:
        logger.error(f"Error in process_email_campaign for {campaign_id}: {e}")
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
            campaign.status = "failed"
            campaign.save()
        except:
            pass
        return f"Error in campaign {campaign_id}: {e}"

    finally:
        connection.close()
