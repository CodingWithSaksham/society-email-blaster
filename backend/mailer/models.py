from django.db import models
from django.contrib.auth.models import User
import uuid
import os


def excel_file_path(instance, filename):
    # Generate a unique path for uploaded Excel files
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("excel_files", filename)


class EmailCampaign(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    html_template = models.TextField()
    excel_file = models.FileField(upload_to=excel_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_emails = models.IntegerField(default=0)
    sent_emails = models.IntegerField(default=0)
    failed_emails = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class TagMapping(models.Model):
    campaign = models.ForeignKey(
        EmailCampaign, on_delete=models.CASCADE, related_name="tag_mappings"
    )
    template_tag = models.CharField(
        max_length=255
    )  # Tag in HTML template (e.g., {{name}})
    excel_header = models.CharField(max_length=255)  # Corresponding Excel column header

    def __str__(self):
        return f"{self.template_tag} -> {self.excel_header}"


class EmailLog(models.Model):
    campaign = models.ForeignKey(
        EmailCampaign, on_delete=models.CASCADE, related_name="email_logs"
    )
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Email to {self.recipient_email} ({self.sent_at})"
