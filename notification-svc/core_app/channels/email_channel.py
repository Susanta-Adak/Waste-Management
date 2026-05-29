import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .base_channel import NotificationSender
from ..models import Notification, NotificationStatus

logger = logging.getLogger(__name__)


class EmailChannel(NotificationSender):
    def send(self, notification: Notification) -> bool:
        try:
            send_mail(
                subject=notification.subject or f"[{notification.notification_type}] Notification",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_contact],
                fail_silently=False,
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            return True
        except Exception as exc:
            logger.error("Email send failed for notification %s: %s", notification.id, exc)
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(exc)
            notification.save(update_fields=['status', 'error_message'])
            return False
