import uuid
from django.db import models


class NotificationType(models.TextChoices):
    WASTE_COLLECTION = 'WASTE_COLLECTION', 'Waste Collection'
    BIN_FULL = 'BIN_FULL', 'Bin Full'
    PAYMENT = 'PAYMENT', 'Payment'
    ALERT = 'ALERT', 'Alert'
    SYSTEM = 'SYSTEM', 'System'


class NotificationChannel(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push Notification'


class NotificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'
    DELIVERED = 'DELIVERED', 'Delivered'


class NotificationTemplate(models.Model):
    """Stores message templates per notification type and channel."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    subject_template = models.CharField(max_length=255, blank=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['notification_type', 'channel']

    def __str__(self):
        return f"{self.name} ({self.notification_type}/{self.channel})"


class Notification(models.Model):
    """Audit log of every notification dispatched."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    recipient_id = models.CharField(max_length=100, db_index=True)
    recipient_contact = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification_type', 'status']),
        ]

    def __str__(self):
        return f"{self.notification_type} → {self.recipient_id} [{self.status}]"


class NotificationPreference(models.Model):
    """Per-user opt-in/out settings for each notification type and channel."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_id', 'notification_type', 'channel']

    def __str__(self):
        state = 'ON' if self.is_enabled else 'OFF'
        return f"{self.user_id} | {self.notification_type} via {self.channel} [{state}]"
