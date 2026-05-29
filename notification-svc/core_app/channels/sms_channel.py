import logging

from django.conf import settings
from django.utils import timezone

from .base_channel import NotificationSender
from ..models import Notification, NotificationStatus

logger = logging.getLogger(__name__)


class SMSChannel(NotificationSender):
    def send(self, notification: Notification) -> bool:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=notification.message,
                from_=settings.TWILIO_FROM_NUMBER,
                to=notification.recipient_contact,
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            return True
        except Exception as exc:
            logger.error("SMS send failed for notification %s: %s", notification.id, exc)
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(exc)
            notification.save(update_fields=['status', 'error_message'])
            return False
