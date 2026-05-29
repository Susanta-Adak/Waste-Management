import logging

from django.conf import settings
from django.utils import timezone

from .base_channel import NotificationSender
from ..models import Notification, NotificationStatus

logger = logging.getLogger(__name__)


class PushChannel(NotificationSender):
    """Sends push notifications via Firebase Cloud Messaging."""

    def send(self, notification: Notification) -> bool:
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging

            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)

            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.subject,
                    body=notification.message,
                ),
                token=notification.recipient_contact,
            )
            messaging.send(message)
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            return True
        except Exception as exc:
            logger.error("Push send failed for notification %s: %s", notification.id, exc)
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(exc)
            notification.save(update_fields=['status', 'error_message'])
            return False
