import re
import pandas as pd
import base64
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from django.conf import settings

logger = logging.getLogger(__name__)


def extract_tags_from_template(html_template: str) -> list[str]:
    """Extract tags like {{tag}} from HTML template"""
    tag_pattern = re.compile(r"{{\s*(.*?)\s*}}")
    tags = tag_pattern.findall(html_template)
    tags_set = {tag.strip() for tag in tags}
    logger.debug(f"Extracted tags from template: {tags_set}")
    return list(tags_set)


def parse_excel_file(file_path: str) -> pd.DataFrame:
    """Parse Excel file and return DataFrame"""
    try:
        df = pd.read_excel(file_path)
        logger.debug(f"Excel file parsed with columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Error parsing Excel file: {e}")
        raise ValueError(f"Error parsing Excel file: {e}")


def validate_template_and_headers(html_template: str, df: pd.DataFrame) -> None:
    """
    Ensure that template tags match exactly the DataFrame columns (excluding 'email', which must exist).
    Raises ValueError listing missing tags/headers if mismatch.
    """
    tags = extract_tags_from_template(html_template)
    headers = list(df.columns)
    headers_lower = {h.lower(): h for h in headers}

    logger.debug(f"Validating tags {tags} against headers {headers}")

    # 'email' must always be present
    if "email" not in headers_lower:
        error_msg = "Excel file must contain an 'email' column"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Compare tag set (lowercased) against headers (lowercased)
    missing_in_excel = [t for t in tags if t.lower() not in headers_lower]
    missing_in_template = [
        h
        for h, orig in headers_lower.items()
        if h not in {t.lower() for t in tags} and h != "email"
    ]

    if missing_in_excel or missing_in_template:
        msg_parts = []
        if missing_in_excel:
            msg_parts.append(f"Missing columns for tags: {', '.join(missing_in_excel)}")
        if missing_in_template:
            msg_parts.append(
                f"Missing tags for columns: {', '.join(missing_in_template)}"
            )
        error_msg = " ; ".join(msg_parts)
        logger.error(f"Validation error: {error_msg}")
        raise ValueError(error_msg)


def replace_tags_in_template(html_template: str, df_row: pd.Series) -> str:
    """Replace tags in HTML template with values from a DataFrame row"""
    content = html_template
    tags = extract_tags_from_template(html_template)
    for tag in tags:
        # case-insensitive lookup
        val = None
        for col in df_row.index:
            if col.lower() == tag.lower():
                val = df_row[col]
                break
        if pd.isna(val) or val is None:
            replacement = ""
        else:
            replacement = str(val)
        # replace all occurrences
        content = re.sub(rf"{{{{\s*{re.escape(tag)}\s*}}}}", replacement, content)
    logger.debug(f"Replaced content for row: {content[:50]}...")
    return content


def send_email_with_gmail_api(
    user_credentials, to_email: str, subject: str, html_content: str
) -> tuple[bool, str | None]:
    """Send email using Gmail API"""
    try:
        creds = Credentials(
            token=user_credentials.access_token,
            refresh_token=user_credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        )
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(html_content, "html")
        message["to"] = to_email
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        logger.info(f"Email sent to {to_email}: id {sent.get('id')}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False, str(e)
